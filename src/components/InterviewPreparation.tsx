import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Upload, FileText, Brain, Download, Edit3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export default function InterviewPreparation() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [candidateProfile, setCandidateProfile] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCvFile(file);
    }
  };

  const handleAnalyze = async () => {
    if (!cvFile) return;
    setIsAnalyzing(true);
    setAiSuggestions(null);
    try {
      const form = new FormData();
      form.append("profile", candidateProfile);
      form.append("cv_file", cvFile);
      const res = await fetch("/api/prep/", { method: "POST", body: form });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Analyze failed");
      }
      const data = await res.json();
      setAiSuggestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExportPdf = async () => {
    if (!aiSuggestions) {
      alert("Нет данных для генерации отчета. Сначала проанализируйте CV.");
      return;
    }

    try {
      const doc = new jsPDF();

            const fontResponse = await fetch('/fonts/Roboto-Regular.ttf');
      const fontBlob = await fontResponse.blob();
      const fontData = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(fontBlob);
      });

      const fontBase64 = fontData.split(',')[1];

      doc.addFileToVFS('Roboto-Regular.ttf', fontBase64);
      doc.addFont('Roboto-Regular.ttf', 'Roboto', 'normal');

      doc.setFont('Roboto', 'normal');

      doc.setFontSize(18);
      doc.text("AI-Generated Interview Guide", 14, 20);

      doc.setFontSize(14);
      doc.text("Key Topics to Cover", 14, 35);

      autoTable(doc, {
        startY: 40,
        body: aiSuggestions.keyTopics.map((topic: string) => [topic]),
        theme: 'plain',
        styles: {
          font: 'Roboto', // 4. Указываем шрифт для таблицы
          fontSize: 10
        },
      });

      const firstTableY = (doc as any).lastAutoTable.finalY || 60;

      const tableData = aiSuggestions.suggestedQuestions.flatMap((category: any) =>
        category.questions.map((question: string) => [category.category, question])
      );

      autoTable(doc, {
        startY: firstTableY + 10,
        head: [['Category', 'Question']],
        body: tableData,
        theme: 'grid',
        headStyles: {
          fillColor: [41, 128, 185],
          font: 'Roboto'
        },
        bodyStyles: {
          font: 'Roboto'
        }
      });

      doc.save("Interview_Preparation_Guide.pdf");

    } catch (error) {
      console.error("Критическая ошибка при создании PDF:", error);
      alert("Произошла ошибка при генерации PDF. Проверьте консоль.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5 text-primary" />
              <span>Upload Candidate CV</span>
            </CardTitle>
            <CardDescription>
              Upload the candidate's CV in PDF or DOCX format
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
              <input
                type="file"
                id="cv-upload"
                accept=".pdf,.docx"
                onChange={handleFileUpload}
                className="hidden"
              />
              <label htmlFor="cv-upload" className="cursor-pointer">
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-sm text-muted-foreground mb-2">
                  {cvFile ? cvFile.name : "Click to upload CV"}
                </p>
                <p className="text-xs text-muted-foreground">
                  PDF or DOCX up to 10MB
                </p>
              </label>
            </div>
            {cvFile && (
              <Badge variant="secondary" className="mt-4">
                ✓ {cvFile.name} uploaded
              </Badge>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Edit3 className="w-5 h-5 text-accent" />
              <span>Candidate Profile</span>
            </CardTitle>
            <CardDescription>
              Required Candidate Profile and Recruiter’s Feedback
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="E.g., Senior Frontend Developer with 5+ years experience in React, TypeScript, and team leadership. Looking for someone who can architect scalable solutions and mentor junior developers..."
              value={candidateProfile}
              onChange={(e) => setCandidateProfile(e.target.value)}
              className="min-h-[120px] resize-none"
            />
          </CardContent>
        </Card>
      </div>

      {/* Generate Button */}
      <div className="text-center">
        <Button
          onClick={handleAnalyze}
          disabled={!cvFile || !candidateProfile || isAnalyzing}
          className="bg-gradient-primary hover:shadow-glow transition-all duration-300 px-8"
          size="lg"
        >
          {isAnalyzing ? (
            <>
              <Brain className="w-5 h-5 mr-2 animate-spin" />
              Analyzing with AI...
            </>
          ) : (
            <>
              <Brain className="w-5 h-5 mr-2" />
              Generate Interview Preparation
            </>
          )}
        </Button>
      </div>

      {/* AI Suggestions */}
      {aiSuggestions && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-bold">AI-Generated Interview Guide</h3>
            <Button variant="outline" size="sm" onClick={handleExportPdf}>
              <Download className="w-4 h-4 mr-2" />
              Export PDF
            </Button>
          </div>

          {/* Key Topics */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Key Topics to Cover</CardTitle>
              <CardDescription>
                Based on the candidate's CV and your requirements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {aiSuggestions.keyTopics.map((topic: string, index: number) => (
                  <Badge key={index} variant="secondary" className="px-3 py-1">
                    {topic}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Suggested Questions */}
          <div className="space-y-4">
            {aiSuggestions.suggestedQuestions.map((category: any, index: number) => (
              <Card key={index} className="shadow-card">
                <CardHeader>
                  <CardTitle className="text-lg">{category.category}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {category.questions.map((question: string, qIndex: number) => (
                      <div key={qIndex} className="flex items-start space-x-3 p-3 bg-muted/50 rounded-lg">
                        <span className="text-primary font-semibold text-sm mt-1">
                          Q{qIndex + 1}
                        </span>
                        <p className="text-sm leading-relaxed">{question}</p>
                        <Button variant="ghost" size="sm" className="ml-auto">
                          <Edit3 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}