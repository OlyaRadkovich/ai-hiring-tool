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
  Building,
  UserCheck,
  ClipboardList,
  FileJson,
  BookUser
} from "lucide-react";
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
};


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
    setAnalysisResults(null);
    try {
      const form = new FormData();
      form.append("cv_file", cvFile);
      form.append("video_link", videoLink);
      form.append("competency_matrix_link", competencyMatrixLink);
      form.append("department_values_link", departmentValuesLink);
      form.append("employee_portrait_link", employeePortraitLink);
      form.append("job_requirements_link", jobRequirementsLink);

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

  const handleExportPdf = async () => {
    if (!analysisResults || !analysisResults.report) return;
    setIsExporting(true);

    try {
        const doc = new jsPDF();
        const report = analysisResults.report;

        const fontNormalResponse = await fetch('/fonts/Roboto-Light.ttf');
        const fontNormalBuffer = await fontNormalResponse.arrayBuffer();

        const fontBoldResponse = await fetch('/fonts/Roboto-SemiBold.ttf');
        const fontBoldBuffer = await fontBoldResponse.arrayBuffer();

        doc.addFileToVFS('Roboto-Light.ttf', arrayBufferToBase64(fontNormalBuffer));
        doc.addFont('Roboto-Light.ttf', 'Roboto', 'normal');

        doc.addFileToVFS('Roboto-SemiBold.ttf', arrayBufferToBase64(fontBoldBuffer));
        doc.addFont('Roboto-SemiBold.ttf', 'Roboto', 'bold');

        doc.setFont('Roboto');

        doc.setFontSize(14);
        doc.setFont('Roboto', 'bold');
        doc.text(`Фидбек на кандидата ${report.candidate_info.full_name}`, 15, 15);

        const body = [
          [{ content: `**AI-generated summary:** ${report.ai_summary}`, colSpan: 2, styles: { fontStyle: 'normal' } }],
          [{ content: ' ', colSpan: 2, styles: { minCellHeight: 5 } }],

          [{ content: '**1. Информация о кандидате**', colSpan: 2, styles: { fontSize: 12, fontStyle: 'bold' } }],
          [{ content: '**1.1 Опыт**', colSpan: 2, styles: { fontStyle: 'bold' } }],
          ['**● Количество лет опыта:**', report.candidate_info.experience_years],
          ['**● Стеки технологий:**', report.candidate_info.tech_stack.join(', ')],
          ['**● Проекты:**', report.candidate_info.projects.join(', ')],
          ['**● Домены:**', report.candidate_info.domains.join(', ')],
          ['**● Задачи, которые выполнял(а):**', report.candidate_info.tasks.join(', ')],

          [{ content: '**1.2 Технические знания**', colSpan: 2, styles: { fontStyle: 'bold' } }],
          ['**● Темы, которые затрагивались на собеседовании:**', report.interview_analysis.topics.join(', ')],
          ['**● Тех задание:**', report.interview_analysis.tech_assignment],
          ['**● Оценка знаний по этим темам:**', report.interview_analysis.knowledge_assessment],

          [{ content: '**1.3 Коммуникационные навыки**', colSpan: 2, styles: { fontStyle: 'bold' } }],
          ['**● Оценка коммуникационных навыков:**', report.communication_skills.assessment],

          [{ content: '**1.4 Иностранные языки**', colSpan: 2, styles: { fontStyle: 'bold' } }],
          ['**● Уровень владения иностранными языками:**', report.foreign_languages.assessment],
          [{ content: ' ', colSpan: 2, styles: { minCellHeight: 5 } }],

          [{ content: '**2. Соответствие команде**', colSpan: 2, styles: { fontSize: 12, fontStyle: 'bold' } }],
          ['**● Насколько кандидат соответствует ценностям и взглядам команды:**', report.team_fit],
          [{ content: ' ', colSpan: 2, styles: { minCellHeight: 5 } }],

          [{ content: '**3. Дополнительная информация**', colSpan: 2, styles: { fontSize: 12, fontStyle: 'bold' } }],
          ...report.additional_information.length > 0
            ? report.additional_information.map((info: string) => [{ content: `○ ${info}`, colSpan: 2, styles: { fontStyle: 'normal' } }])
            : [[{ content: 'Нет.', colSpan: 2, styles: { fontStyle: 'normal' } }]],
          [{ content: ' ', colSpan: 2, styles: { minCellHeight: 5 } }],

          [{ content: '**4. Заключение**', colSpan: 2, styles: { fontSize: 12, fontStyle: 'bold' } }],
          [{ content: `1. ${report.conclusion.recommendation}`, colSpan: 2, styles: { fontStyle: 'normal' } }],
          [{ content: `2. По уровню знаний оцениваем его на уровень ${report.conclusion.assessed_level}`, colSpan: 2, styles: { fontStyle: 'normal' } }],
          [{ content: `3. ${report.conclusion.summary}`, colSpan: 2, styles: { fontStyle: 'normal' } }],
          [{ content: ' ', colSpan: 2, styles: { minCellHeight: 5 } }],

          [{ content: '**5. Рекомендации для кандидата**', colSpan: 2, styles: { fontSize: 12, fontStyle: 'bold' } }],
          ...report.recommendations_for_candidate.length > 0
            ? report.recommendations_for_candidate.map((rec: string) => [{ content: `● ${rec}`, colSpan: 2, styles: { fontStyle: 'normal' } }])
            : [[{ content: 'Рекомендации не сгенерированы.', colSpan: 2, styles: { fontStyle: 'normal' } }]],
        ];

        autoTable(doc, {
            startY: 25,
            body: body,
            theme: 'plain',
            styles: {
                font: 'Roboto',
                fontSize: 10,
                cellPadding: { top: 0, right: 0, bottom: 1, left: 0 },
            },
            columnStyles: {
                0: { fontStyle: 'bold', cellWidth: 70 }, // Первая колонка жирная
                1: { fontStyle: 'normal' }, // Вторая колонка обычная
            },
            didParseCell: (data) => {
                if (typeof data.cell.text[0] === 'string') {
                    data.cell.text = data.cell.text[0].replace(/\*\*/g, '');
                }
            }
        });

        const fullName = report.candidate_info.full_name.replace(/\s+/g, '_');
        doc.save(`Interview_Report_${fullName}.pdf`);

    } catch (error) {
      console.error("Ошибка при создании PDF:", error);
      alert("Не удалось создать PDF файл.");
    } finally {
      setIsExporting(false);
    }
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
          </CardHeader>
          <CardContent className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
                <Label htmlFor="competency-matrix-link" className="flex items-center space-x-2"><FileText className="w-4 h-4" /><span>Матрица компетенций</span></Label>
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

      <>
        {isProcessing && !analysisResults && (
          <div className="text-center py-10">
              <p>Идет анализ... Это может занять несколько минут.</p>
              <Progress value={50} className="w-1-2 mx-auto mt-4 animate-pulse" />
          </div>
        )}

        {analysisResults && analysisResults.report && (
          <div className="p-6 border rounded-lg mt-6 bg-white shadow-sm font-sans">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                Фидбек на кандидата {analysisResults.report.candidate_info.full_name}
              </h2>
              <Button onClick={handleExportPdf} disabled={isExporting}>
                {isExporting ? 'Экспорт...' : <><Download className="w-4 h-4 mr-2" /> Скачать PDF</>}
              </Button>
            </div>
            <div className="space-y-3 text-sm text-gray-800">
              <p><b>AI-generated summary:</b> {analysisResults.report.ai_summary}</p>

              <h3 className="text-base font-bold pt-2">1. Информация о кандидате</h3>
              <div className="pl-4">
                <p className="font-semibold">1.1 Опыт</p>
                <div className="pl-4 space-y-1">
                    <p>• <b>Количество лет опыта:</b> {analysisResults.report.candidate_info.experience_years}</p>
                    <p>• <b>Стеки технологий:</b> {analysisResults.report.candidate_info.tech_stack.join(', ')}</p>
                    <p>• <b>Проекты:</b> {analysisResults.report.candidate_info.projects.join(', ')}</p>
                    <p>• <b>Домены:</b> {analysisResults.report.candidate_info.domains.join(', ')}</p>
                    <p>• <b>Задачи, которые выполнял(а) на предыдущих проектах:</b> {analysisResults.report.candidate_info.tasks.join(', ')}</p>
                </div>

                <p className="font-semibold mt-2">1.2 Технические знания</p>
                <div className="pl-4 space-y-1">
                    <p>• <b>Темы, которые затрагивались на собеседовании:</b> {analysisResults.report.interview_analysis.topics.join(', ')}</p>
                    <p>• <b>Тех задание:</b> {analysisResults.report.interview_analysis.tech_assignment}</p>
                    <p>• <b>Оценка знаний по этим темам:</b> {analysisResults.report.interview_analysis.knowledge_assessment}</p>
                </div>

                <p className="font-semibold mt-2">1.3 Коммуникационные навыки</p>
                <div className="pl-4 space-y-1">
                    <p>• <b>Оценка коммуникационных навыков:</b> {analysisResults.report.communication_skills.assessment}</p>
                </div>

                <p className="font-semibold mt-2">1.4 Иностранные языки</p>
                <div className="pl-4 space-y-1">
                  <p>• <b>Уровень владения иностранными языками:</b> {analysisResults.report.foreign_languages.assessment}</p>
                </div>
              </div>

              <h3 className="text-base font-bold pt-2">2. Соответствие команде</h3>
              <p><b>Насколько кандидат соответствует ценностям и взглядам команды:</b> {analysisResults.report.team_fit}</p>

              <h3 className="text-base font-bold pt-2">3. Дополнительная информация</h3>
              <div className="pl-4 space-y-1">
                {analysisResults.report.additional_information.length > 0 ? (
                  analysisResults.report.additional_information.map((info: string, i: number) => <p key={i}>○ {info}</p>)
                ) : (
                  <p className="italic">Нет.</p>
                )}
              </div>

              <h3 className="text-base font-bold pt-2">4. Заключение</h3>
              <div className="pl-4 space-y-1">
                <p>1. {analysisResults.report.conclusion.recommendation}</p>
                <p>2. По уровню знаний оцениваем его на уровень {analysisResults.report.conclusion.assessed_level}</p>
                <p>3. {analysisResults.report.conclusion.summary}</p>
              </div>

              <h3 className="text-base font-bold pt-2">5. Рекомендации для кандидата</h3>
                {analysisResults.report.recommendations_for_candidate.length > 0 ? (
                    <ul className="pl-4 list-disc list-inside space-y-1">
                        {analysisResults.report.recommendations_for_candidate.map((rec: string, i: number) => <li key={i}>{rec}</li>)}
                    </ul>
                ) : (
                    <p className="pl-4 text-gray-500 italic">Рекомендации не сгенерированы.</p>
                )}
            </div>
          </div>
        )}
      </>
    </div>
  );
}