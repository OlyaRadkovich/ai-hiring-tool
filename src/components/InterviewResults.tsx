import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Video,
  Upload,
  Brain,
  Download,
  FileText,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  Target,
  FileJson,
  BookUser,
  Building,
  UserCheck,
  ClipboardList
} from "lucide-react";

export default function InterviewResults() {

  const [cvFile, setCvFile] = useState<File | null>(null);
  const [videoLink, setVideoLink] = useState("");
  const [competencyMatrixLink, setCompetencyMatrixLink] = useState("https://docs.google.com/spreadsheets/d/1TkBmT4XQ-nQrdJ2ALGLwXb99wlcFIPwhgah3ZTafOwE/edit?usp=drive_link");
  const [departmentValuesLink, setDepartmentValuesLink] = useState("https://docs.google.com/spreadsheets/d/1MEQq1yqlWINXuA3-zc9dVhUeuBysSmf7D_w9goPNhLg/edit?usp=drive_link");
  const [employeePortraitLink, setEmployeePortraitLink] = useState("https://docs.google.com/spreadsheets/d/1dtP5BHysvSffMt8OrXaVo5a1jcuO4o-yq3h_ITAImIk/edit?usp=drive_link");
  const [jobRequirementsLink, setJobRequirementsLink] = useState("https://docs.google.com/spreadsheets/d/1w-DpZkCCBt2C0XBhXrdt9rgZ9WeNI6V15Iv55E5QBcw/edit?usp=drive_link");

  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [isExporting, setIsExporting] = useState(false);

  const handleFileChange = (setter: React.Dispatch<React.SetStateAction<File | null>>) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setter(file);
    }
  };

  const handleAnalyzeInterview = async () => {
    if (!cvFile || !videoLink) {
        alert("Пожалуйста, загрузите CV и укажите ссылку на видеозапись.");
        return;
    }

    setIsProcessing(true);
    try {
      const form = new FormData();

      form.append("cv_file", cvFile);

      form.append("video_link", videoLink);
      form.append("competency_matrix_link", competencyMatrixLink);
      form.append("department_values_link", departmentValuesLink);
      form.append("employee_portrait_link", employeePortraitLink);
      form.append("job_requirements_link", jobRequirementsLink);

      // !! ВАЖНО: URL эндпоинта и названия полей в FormData
      //    должны будут соответствовать бэкенду, когда мы его обновим.
      const res = await fetch("/api/results/", { method: "POST", body: form });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Analyze failed");
      }
      const data = await res.json();
      setAnalysisResults(data);
    } catch (err: any) {
      console.error(err);
      alert(`Произошла ошибка: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExportDocx = async () => {
    if (!analysisResults) return;
    setIsExporting(true);
    try {
      const response = await fetch("/api/results/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(analysisResults),
      });

      if (!response.ok) {
        throw new Error("Не удалось сгенерировать DOCX отчет.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Interview_Report.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Ошибка при экспорте DOCX:", error);
    } finally {
      setIsExporting(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <h2 className="text-3xl font-bold">Анализ Результатов Интервью</h2>
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2"><BookUser className="w-5 h-5 text-primary" /><span>CV Кандидата</span></CardTitle>
            <CardDescription>Загрузите резюме в формате .txt, .pdf или .docx</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
              <input type="file" id="cv-upload" accept=".pdf,.docx, .txt" onChange={handleFileChange(setCvFile)} className="hidden" />
              <label htmlFor="cv-upload" className="cursor-pointer">
                <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground mb-2">{cvFile ? cvFile.name : "Нажмите для загрузки CV"}</p>
              </label>
            </div>
            {cvFile && <Badge variant="secondary" className="mt-3">✓ {cvFile.name} загружен</Badge>}
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2"><Video className="w-5 h-5 text-primary" /><span>Видеозапись собеседования</span></CardTitle>
            <CardDescription>Вставьте ссылку на видео в Google Drive</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Label htmlFor="video-link">Ссылка на видео</Label>
            <Input id="video-link" type="url" placeholder="https://drive.google.com/file/d/..." value={videoLink} onChange={(e) => setVideoLink(e.target.value)} />
          </CardContent>
        </Card>

        <Card className="shadow-card md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2"><FileJson className="w-5 h-5 text-accent" /><span>Дополнительные материалы (Google Drive)</span></CardTitle>
            <CardDescription>Ссылки на Google-таблицы с критериями.</CardDescription>
            <CardDescription>Вы можете использовать стандартные или указать свои.</CardDescription>
            <CardDescription>ВАЖНО! При изменении ссылки убедитесь, что документ является Google-таблицей и находится в папке, куда у приложения есть доступ уровня Contributor/Editor.</CardDescription>
            <CardDescription>Чтобы открыть доступ, добавьте почту приложения в share. Почта: ai-hiring-tool-service@ai-hiring-tool.iam.gserviceaccount.com</CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
                <Label htmlFor="competency-matrix-link" className="flex items-center space-x-2"><FileText className="w-4 h-4" /><span>Матрица компетенций QA/AQA</span></Label>
                <Input id="competency-matrix-link" type="url" value={competencyMatrixLink} onChange={(e) => setCompetencyMatrixLink(e.target.value)} />
            </div>
            <div className="space-y-2">
                <Label htmlFor="department-values-link" className="flex items-center space-x-2"><Building className="w-4 h-4" /><span>Ценности департамента</span></Label>
                <Input id="department-values-link" type="url" value={departmentValuesLink} onChange={(e) => setDepartmentValuesLink(e.target.value)} />
            </div>
            <div className="space-y-2">
                <Label htmlFor="employee-portrait-link" className="flex items-center space-x-2"><UserCheck className="w-4 h-4" /><span>Портрет сотрудника</span></Label>
                <Input id="employee-portrait-link" type="url" value={employeePortraitLink} onChange={(e) => setEmployeePortraitLink(e.target.value)} />
            </div>
            <div className="space-y-2">
                <Label htmlFor="job-requirements-link" className="flex items-center space-x-2"><ClipboardList className="w-4 h-4" /><span>Требования к вакансии</span></Label>
                <Input id="job-requirements-link" type="url" value={jobRequirementsLink} onChange={(e) => setJobRequirementsLink(e.target.value)} />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="text-center pt-4">
        <Button onClick={handleAnalyzeInterview} disabled={!cvFile || !videoLink || isProcessing} className="bg-gradient-primary hover:shadow-glow transition-all duration-300 px-8 py-6 text-lg" size="lg">
          {isProcessing ? (
            <><Brain className="w-6 h-6 mr-3 animate-spin" /><span>Обработка...</span></>
          ) : (
            <><Brain className="w-6 h-6 mr-3" /><span>Запустить AI-анализ</span></>
          )}
        </Button>
      </div>

      {analysisResults && (
        <div className="space-y-8 pt-6">
        </div>
      )}
    </div>
  );
}