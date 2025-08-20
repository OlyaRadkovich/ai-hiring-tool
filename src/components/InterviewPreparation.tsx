import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Upload, FileText, Brain, Download, Edit3, CheckCircle, AlertTriangle, XCircle, User, FileCheck, Lightbulb, HeartHandshake, BookOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// Определяем типы для нового ответа от API
interface MatchItem {
  criterion: string;
  match: 'full' | 'partial' | 'none' | string; // string для гибкости
  comment: string;
}

interface Conclusion {
  summary: string;
  recommendations: string;
  interview_topics: string[];
  values_assessment: string;
}

interface Report {
  matching_table: MatchItem[];
  candidate_profile: string;
  conclusion: Conclusion;
}

interface AnalysisResponse {
  report: Report;
  message?: string;
}

// Компонент для иконок соответствия
const MatchIcon = ({ match }: { match: MatchItem['match'] }) => {
  switch (match) {
    case 'full':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'partial':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    case 'none':
      return <XCircle className="w-5 h-5 text-red-500" />;
    default:
      return null;
  }
};


export default function InterviewPreparation() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [candidateProfile, setCandidateProfile] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCvFile(file);
    }
  };

  const handleAnalyze = async () => {
    if (!cvFile) return;
    setIsAnalyzing(true);
    setAnalysisResponse(null);
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
      setAnalysisResponse(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExportPdf = async () => {
    if (!analysisResponse?.report) {
      alert("Нет данных для генерации отчета.");
      return;
    }
    const { report } = analysisResponse;
    const doc = new jsPDF();

    // Логика добавления шрифтов (оставлена без изменений)
    try {
      const fontResponse = await fetch('/fonts/Roboto-Regular.ttf');
      const fontBlob = await fontResponse.blob();
      const fontData = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(fontBlob);
      });
      const fontBase64 = fontData.split(',')[1];

      const fontBoldResponse = await fetch('/fonts/Roboto-Bold.ttf');
      const fontBoldBlob = await fontBoldResponse.blob();
      const fontBoldData = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(fontBoldBlob);
      });
      const fontBoldBase64 = fontBoldData.split(',')[1];

      doc.addFileToVFS('Roboto-Regular.ttf', fontBase64);
      doc.addFont('Roboto-Regular.ttf', 'Roboto', 'normal');
      doc.addFileToVFS('Roboto-Bold.ttf', fontBoldBase64);
      doc.addFont('Roboto-Bold.ttf', 'Roboto', 'bold');
    } catch (error) {
        console.error("Не удалось загрузить шрифты, будет использован стандартный шрифт.", error);
    }

    doc.setFont('Roboto', 'bold');
    doc.setFontSize(18);
    doc.text("AI Interview Preparation Report", 14, 20);

    doc.setFontSize(12);
    doc.text(`Candidate Profile: ${report.candidate_profile}`, 14, 30);

    // Таблица соответствия
    doc.setFont('Roboto', 'bold');
    doc.setFontSize(14);
    doc.text("Compliance with Key Criteria", 14, 45);
    autoTable(doc, {
      startY: 50,
      head: [['Criterion', 'Match', 'Comment']],
      body: report.matching_table.map(item => [item.criterion, item.match, item.comment]),
      theme: 'grid',
      styles: { font: 'Roboto', fontSize: 10 },
      headStyles: { fillColor: [41, 128, 185], fontStyle: 'bold' },
    });

    let lastY = (doc as any).lastAutoTable.finalY + 15;

    // Функция для добавления текстовых блоков
    const addTextBlock = (title: string, content: string) => {
      if (lastY > 260) {
          doc.addPage();
          lastY = 20;
      }
      doc.setFont('Roboto', 'bold');
      doc.setFontSize(14);
      doc.text(title, 14, lastY);
      doc.setFont('Roboto', 'normal');
      doc.setFontSize(10);
      const splitText = doc.splitTextToSize(content, 180);
      doc.text(splitText, 14, lastY + 7);
      lastY += 10 + splitText.length * 5; // Динамический расчет высоты
    };

    addTextBlock("Overall Conclusion", report.conclusion.summary);
    addTextBlock("Recommendations for Development", report.conclusion.recommendations);
    addTextBlock("Topics for Technical Interview", report.conclusion.interview_topics.join('\n'));
    addTextBlock("Values Alignment Assessment", report.conclusion.values_assessment);

    doc.save("Interview_Preparation_Report.pdf");
  };

  const report = analysisResponse?.report;

  return (
    <div className="space-y-6">
      {/* Секция загрузки и анализа (без изменений) */}
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

      {/* НОВЫЙ БЛОК ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ */}
      {report && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-bold">AI Analysis Report</h3>
            <Button variant="outline" size="sm" onClick={handleExportPdf}>
              <Download className="w-4 h-4 mr-2" />
              Export PDF Report
            </Button>
          </div>

          {/* Профиль кандидата */}
          <Card className="shadow-card">
              <CardHeader>
                  <CardTitle className="flex items-center space-x-3">
                      <User className="w-6 h-6 text-primary" />
                      <span>Candidate Profile</span>
                  </CardTitle>
              </CardHeader>
              <CardContent>
                  <Badge variant="default" className="text-base px-4 py-2">{report.candidate_profile}</Badge>
              </CardContent>
          </Card>

          {/* Таблица соответствия */}
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-3">
                  <FileCheck className="w-6 h-6 text-primary" />
                  <span>Compliance with Key Criteria</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">Match</TableHead>
                    <TableHead>Criterion</TableHead>
                    <TableHead>Comment</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {report.matching_table.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">
                        <div className="flex items-center justify-center">
                           <MatchIcon match={item.match} />
                        </div>
                      </TableCell>
                      <TableCell>{item.criterion}</TableCell>
                      <TableCell>{item.comment}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Выводы */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <Lightbulb className="w-6 h-6 text-primary" />
                  <span>Overall Conclusion</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">{report.conclusion.summary}</p>
              </CardContent>
            </Card>
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <BookOpen className="w-6 h-6 text-primary" />
                  <span>Recommendations for Development</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">{report.conclusion.recommendations}</p>
              </CardContent>
            </Card>
          </div>

          <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <HeartHandshake className="w-6 h-6 text-primary" />
                  <span>Values Alignment Assessment</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">{report.conclusion.values_assessment}</p>
              </CardContent>
          </Card>

           <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Topics for Technical Interview</CardTitle>
              <CardDescription>
                Based on the candidate's CV and your requirements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {report.conclusion.interview_topics.map((topic, index) => (
                  <Badge key={index} variant="secondary" className="px-3 py-1">
                    {topic}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}