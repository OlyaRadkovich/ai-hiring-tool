import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
  BookUser,
} from "lucide-react";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import { toast } from "./ui/use-toast";

interface CandidateInfo {
  full_name: string;
  experience_years: string;
  tech_stack: string[];
  projects: string[];
  domains: string[];
  tasks: string[];
}
interface InterviewAnalysis {
  topics: string[];
  tech_assignment: string;
  knowledge_assessment: string;
}
interface CommunicationSkills {
  assessment: string;
}
interface ForeignLanguages {
  assessment: string;
}
interface FinalConclusion {
  recommendation: string;
  assessed_level: string;
  summary: string;
}
interface FullReport {
  ai_summary: string;
  candidate_info: CandidateInfo;
  interview_analysis: InterviewAnalysis;
  communication_skills: CommunicationSkills;
  foreign_languages: ForeignLanguages;
  team_fit: string;
  additional_information: string[];
  conclusion: FinalConclusion;
  recommendations_for_candidate: string[];
}
interface ResultsAnalysisResponse {
  message: string;
  success: boolean;
  report: FullReport;
}
interface InterviewResultsProps {
  cachedData: ResultsAnalysisResponse | undefined;
  updateCache: (data: ResultsAnalysisResponse | undefined) => void;
  isProcessing: boolean;
  setIsProcessing: (status: boolean) => void;
  startAnalysisTask: (taskId: string) => void;
}

const arrayBufferToBase64 = (buffer: ArrayBuffer) => {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
};

export default function InterviewResults({
  cachedData,
  updateCache,
  isProcessing,
  setIsProcessing,
  startAnalysisTask,
}: InterviewResultsProps) {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [videoLink, setVideoLink] = useState("");
  const [competencyMatrixLink, setCompetencyMatrixLink] = useState(
    "https://docs.google.com/spreadsheets/d/1VzwMPfgBn6xB0xKnJ-DD-0bkBQDOvbjihwuT6FKo8qY/edit?usp=drive_link"
  );
  const [departmentValuesLink, setDepartmentValuesLink] = useState(
    "https://docs.google.com/spreadsheets/d/1KX1ihfOTm7OGEI942cEii4dj9T8VvtmUhisE49WYAUo/edit?usp=drive_link"
  );
  const [employeePortraitLink, setEmployeePortraitLink] = useState(
    "https://docs.google.com/spreadsheets/d/1hIksOP9zcBy5fFZ12SyA_lc6xsL0EXHPC2Y86YykVPI/edit?usp=drive_link"
  );
  const [jobRequirementsLink, setJobRequirementsLink] = useState(
    "https://docs.google.com/spreadsheets/d/1JOYzYmAtaPzHHuN2CvdrCXn_L30bBNlikJ5K0mRt-HE/edit?usp=drive_link"
  );
  const [isExporting, setIsExporting] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setCvFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (
      file &&
      (file.type === "application/pdf" ||
        file.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        file.type === "text/plain")
    ) {
      setCvFile(file);
    }
  };

  const handleAnalyzeInterview = async () => {
    if (!videoLink) {
      toast({
        title: "Ошибка валидации",
        description: "Пожалуйста, укажите ссылку на видеозапись.",
        variant: "destructive",
      });
      return;
    }

    // 1. Включаем состояние загрузки и очищаем старые результаты
    setIsProcessing(true);
    updateCache(undefined);

    try {
      const form = new FormData();
      if (cvFile) {
        form.append("cv_file", cvFile);
      }
      form.append("video_link", videoLink);
      form.append("competency_matrix_link", competencyMatrixLink);
      form.append("department_values_link", departmentValuesLink);
      form.append("employee_portrait_link", employeePortraitLink);
      form.append("job_requirements_link", jobRequirementsLink);

      const res = await fetch(`${API_BASE_URL}/api/results/`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Не удалось запустить анализ");
      }

      // 2. Получаем job_id из ответа API
      const job = await res.json();
      const { job_id } = job;
      
      if (!job_id) {
        throw new Error("API не вернул ID задачи (job_id).");
      }

      // 3. ПЕРЕДАЕМ ID ЗАДАЧИ НАВЕРХ в Dashboard.tsx, чтобы он начал опрос
      startAnalysisTask(job_id);

      toast({
        title: "Задача принята",
        description: "Анализ запущен в фоновом режиме. Результат появится автоматически.",
      });

    } catch (err: any) {
      console.error("Ошибка при запуске анализа:", err);
      toast({
        title: "Ошибка",
        description: `Не удалось запустить анализ: ${err.message}`,
        variant: "destructive",
      });
      // Если запустить не удалось, выключаем загрузку
      setIsProcessing(false);
    }
    // `finally` блок нам больше не нужен, т.к. состояние загрузки
    // теперь контролируется из Dashboard.tsx
  };

  const handleExportPdf = async () => {
    if (!cachedData || !cachedData.report) return;
    setIsExporting(true);

    try {
      const doc = new jsPDF();
      const report = cachedData.report;

      const fontNormalResponse = await fetch("/fonts/Roboto-Light.ttf");
      const fontNormalBuffer = await fontNormalResponse.arrayBuffer();

      const fontBoldResponse = await fetch("/fonts/Roboto-SemiBold.ttf");
      const fontBoldBuffer = await fontBoldResponse.arrayBuffer();

      doc.addFileToVFS(
        "Roboto-Light.ttf",
        arrayBufferToBase64(fontNormalBuffer)
      );
      doc.addFont("Roboto-Light.ttf", "Roboto", "normal");

      doc.addFileToVFS(
        "Roboto-SemiBold.ttf",
        arrayBufferToBase64(fontBoldBuffer)
      );
      doc.addFont("Roboto-SemiBold.ttf", "Roboto", "bold");

      doc.setFont("Roboto");

      doc.setFontSize(14);
      doc.setFont("Roboto", "bold");
      doc.text(
        `Фидбек на кандидата ${report.candidate_info.full_name}`,
        15,
        15
      );

      const body = [
        [{ content: "AI-generated summary:", styles: { fontStyle: "bold" } }],
        [{ content: report.ai_summary, styles: { fontStyle: "normal" } }],
        [{ content: " ", styles: { minCellHeight: 5 } }],

        [
          {
            content: "1. Информация о кандидате",
            styles: { fontSize: 12, fontStyle: "bold" },
          },
        ],
        [{ content: "1.1 Опыт", styles: { fontStyle: "bold" } }],
        [{ content: "Количество лет опыта:", styles: { fontStyle: "bold" } }],
        [
          {
            content: report.candidate_info.experience_years,
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: "Стеки технологий:", styles: { fontStyle: "bold" } }],
        [
          {
            content: report.candidate_info.tech_stack.join(", "),
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: "Проекты:", styles: { fontStyle: "bold" } }],
        [
          {
            content: report.candidate_info.projects.join(", "),
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: "Домены:", styles: { fontStyle: "bold" } }],
        [
          {
            content: report.candidate_info.domains.join(", "),
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: "Задачи, которые выполнял(а):",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.candidate_info.tasks.join(", "),
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: "1.2 Технические знания",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: "Темы, которые затрагивались на собеседовании:",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.interview_analysis.topics.join(", "),
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: "Тех задание:", styles: { fontStyle: "bold" } }],
        [
          {
            content: report.interview_analysis.tech_assignment,
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: "Оценка знаний по этим темам:",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.interview_analysis.knowledge_assessment,
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: "1.3 Коммуникационные навыки",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: "Оценка коммуникационных навыков:",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.communication_skills.assessment,
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: " ", styles: { minCellHeight: 5 } }],
        [
          {
            content: "1.4 Иностранные языки",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: "Уровень владения иностранными языками:",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.foreign_languages.assessment,
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: " ", styles: { minCellHeight: 5 } }],

        [
          {
            content: "2. Соответствие команде",
            styles: { fontSize: 12, fontStyle: "bold" },
          },
        ],
        [
          {
            content:
              "Насколько кандидат соответствует ценностям и взглядам команды:",
            styles: { fontStyle: "bold" },
          },
        ],
        [
          {
            content: report.team_fit,
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: " ", styles: { minCellHeight: 5 } }],

        [
          {
            content: "3. Дополнительная информация",
            styles: { fontSize: 12, fontStyle: "bold" },
          },
        ],
        ...(report.additional_information.length > 0
          ? report.additional_information.map((info: string) => [
              { content: `○ ${info}`, styles: { fontStyle: "normal" } },
            ])
          : [[{ content: "Нет.", styles: { fontStyle: "normal" } }]]),
        [{ content: " ", styles: { minCellHeight: 5 } }],

        [
          {
            content: "4. Заключение",
            styles: { fontSize: 12, fontStyle: "bold" },
          },
        ],
        [
          {
            content: `1. ${report.conclusion.recommendation}`,
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: `2. По уровню знаний оцениваем его на уровень ${report.conclusion.assessed_level}`,
            styles: { fontStyle: "normal" },
          },
        ],
        [
          {
            content: `3. ${report.conclusion.summary}`,
            styles: { fontStyle: "normal" },
          },
        ],
        [{ content: " ", styles: { minCellHeight: 5 } }],

        [
          {
            content: "5. Рекомендации для кандидата",
            styles: { fontSize: 12, fontStyle: "bold" },
          },
        ],
        ...(report.recommendations_for_candidate.length > 0
          ? report.recommendations_for_candidate.map((rec: string) => [
              { content: `● ${rec}`, styles: { fontStyle: "normal" } },
            ])
          : [
              [
                {
                  content: "Рекомендации не сгенерированы.",
                  styles: { fontStyle: "normal" },
                },
              ],
            ]),
      ];

      autoTable(doc, {
        startY: 25,
        body: body,
        theme: "plain",
        styles: {
          font: "Roboto",
          fontSize: 10,
          cellPadding: { top: 1, right: 0, bottom: 1, left: 0 },
        },
      });

      const fullName = report.candidate_info.full_name.replace(/\s+/g, "_");
      doc.save(`Фидбек на кандидата ${fullName}.pdf`);
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
            <CardTitle className="flex items-center space-x-2">
              <BookUser className="w-5 h-5 text-primary" />
              <span>CV кандидата (опционально)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                isDragging
                  ? "border-primary bg-primary/10"
                  : "border-border hover:border-primary/50"
              }`}
            >
              <input
                type="file"
                id="cv-upload-results"
                accept=".pdf,.docx, .txt"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="cv-upload-results" className="cursor-pointer">
                <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground mb-2">
                  {cvFile
                    ? cvFile.name
                    : "Нажмите или перетащите файл для загрузки (.txt, .pdf, .docx)"}
                </p>
              </label>
            </div>
            {cvFile && (
              <Badge variant="secondary" className="mt-3">
                ✓ {cvFile.name} загружен
              </Badge>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Video className="w-5 h-5 text-primary" />
              <span>Видеозапись собеседования</span>
            </CardTitle>
            <CardDescription>
              Файл с видеозаписью должен находиться в папке InterviewsRecords.
            </CardDescription>
            <CardDescription>
              Путь: QA Common / QAHiringToInnowise / InterviewsRecords.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Label htmlFor="video-link">Ссылка на видео</Label>
            <Input
              id="video-link"
              type="url"
              placeholder="https://drive.google.com/file/d/..."
              value={videoLink}
              onChange={(e) => setVideoLink(e.target.value)}
            />
          </CardContent>
        </Card>

        <Card className="shadow-card md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileJson className="w-5 h-5 text-accent" />
              <span>Дополнительные материалы (Google Drive)</span>
            </CardTitle>
            <CardDescription>
              При изменении ссылки убедитесь, что документ является
              Google-таблицей и находится в папке, к которой у сервиса
              ai-hiring-tool-service@ai-hiring-tool.iam.gserviceaccount.com
              есть доступ уровня Contributor/Editor.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label
                htmlFor="competency-matrix-link"
                className="flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>Матрица компетенций</span>
              </Label>
              <Input
                id="competency-matrix-link"
                type="url"
                value={competencyMatrixLink}
                onChange={(e) => setCompetencyMatrixLink(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="department-values-link"
                className="flex items-center space-x-2"
              >
                <Building className="w-4 h-4" />
                <span>Ценности департамента</span>
              </Label>
              <Input
                id="department-values-link"
                type="url"
                value={departmentValuesLink}
                onChange={(e) => setDepartmentValuesLink(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="employee-portrait-link"
                className="flex items-center space-x-2"
              >
                <UserCheck className="w-4 h-4" />
                <span>Портрет сотрудника</span>
              </Label>
              <Input
                id="employee-portrait-link"
                type="url"
                value={employeePortraitLink}
                onChange={(e) => setEmployeePortraitLink(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="job-requirements-link"
                className="flex items-center space-x-2"
              >
                <ClipboardList className="w-4 h-4" />
                <span>Требования к вакансии</span>
              </Label>
              <Input
                id="job-requirements-link"
                type="url"
                value={jobRequirementsLink}
                onChange={(e) => setJobRequirementsLink(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="text-center pt-4">
        <Button
          onClick={handleAnalyzeInterview}
          disabled={!videoLink || isProcessing}
          className="bg-gradient-primary hover:shadow-glow transition-all duration-300 px-8 py-6 text-lg"
          size="lg"
        >
          {isProcessing ? (
            <>
              <Brain className="w-6 h-6 mr-3 animate-spin" />
              <span>Обработка...</span>
            </>
          ) : (
            <>
              <Brain className="w-6 h-6 mr-3" />
              <span>Запустить AI-анализ</span>
            </>
          )}
        </Button>
      </div>

      <>
        {isProcessing && (
          <div className="text-center py-10">
            <p>Идет анализ... Это может занять несколько минут.</p>
            <Progress value={50} className="w-1-2 mx-auto mt-4 animate-pulse" />
          </div>
        )}

        {cachedData && !isProcessing && (
          <div className="p-6 border rounded-lg mt-6 bg-white shadow-sm font-sans">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                Фидбек на кандидата{" "}
                {cachedData.report.candidate_info.full_name}
              </h2>
              <Button onClick={handleExportPdf} disabled={isExporting}>
                {isExporting ? (
                  "Экспорт..."
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" /> Скачать PDF
                  </>
                )}
              </Button>
            </div>
            <div className="space-y-3 text-sm text-gray-800">
              <p>
                <b>AI-generated summary:</b> {cachedData.report.ai_summary}
              </p>

              <h3 className="text-base font-bold pt-2">
                1. Информация о кандидате
              </h3>
              <div className="pl-4">
                <p className="font-semibold">1.1 Опыт</p>
                <div className="pl-4 space-y-1">
                  <p>
                    • <b>Количество лет опыта:</b>{" "}
                    {cachedData.report.candidate_info.experience_years}
                  </p>
                  <p>
                    • <b>Стеки технологий:</b>{" "}
                    {cachedData.report.candidate_info.tech_stack.join(
                      ", "
                    )}
                  </p>
                  <p>
                    • <b>Проекты:</b>{" "}
                    {cachedData.report.candidate_info.projects.join(
                      ", "
                    )}
                  </p>
                  <p>
                    • <b>Домены:</b>{" "}
                    {cachedData.report.candidate_info.domains.join(", ")}
                  </p>
                  <p>
                    • <b>
                      Задачи, которые выполнял(а) на предыдущих проектах:
                    </b>{" "}
                    {cachedData.report.candidate_info.tasks.join(", ")}
                  </p>
                </div>

                <p className="font-semibold mt-2">1.2 Технические знания</p>
                <div className="pl-4 space-y-1">
                  <p>
                    • <b>Темы, которые затрагивались на собеседовании:</b>{" "}
                    {cachedData.report.interview_analysis.topics.join(
                      ", "
                    )}
                  </p>
                  <p>
                    • <b>Тех задание:</b>{" "}
                    {cachedData.report.interview_analysis.tech_assignment}
                  </p>
                  <p>
                    • <b>Оценка знаний по этим темам:</b>{" "}
                    {
                      cachedData.report.interview_analysis
                        .knowledge_assessment
                    }
                  </p>
                </div>

                <p className="font-semibold mt-2">
                  1.3 Коммуникационные навыки
                </p>
                <div className="pl-4 space-y-1">
                  <p>
                    • <b>Оценка коммуникационных навыков:</b>{" "}
                    {cachedData.report.communication_skills.assessment}
                  </p>
                </div>

                <p className="font-semibold mt-2">1.4 Иностранные языки</p>
                <div className="pl-4 space-y-1">
                  <p>
                    • <b>Уровень владения иностранными языками:</b>{" "}
                    {cachedData.report.foreign_languages.assessment}
                  </p>
                </div>
              </div>

              <h3 className="text-base font-bold pt-2">
                2. Соответствие команде
              </h3>
              <p>
                <b>
                  Насколько кандидат соответствует ценностям и взглядам команды:
                </b>{" "}
                {cachedData.report.team_fit}
              </p>

              <h3 className="text-base font-bold pt-2">
                3. Дополнительная информация
              </h3>
              <div className="pl-4 space-y-1">
                {cachedData.report.additional_information.length > 0 ? (
                  cachedData.report.additional_information.map(
                    (info: string, i: number) => <p key={i}>○ {info}</p>
                  )
                ) : (
                  <p className="italic">Нет.</p>
                )}
              </div>

              <h3 className="text-base font-bold pt-2">4. Заключение</h3>
              <div className="pl-4 space-y-1">
                <p>1. {cachedData.report.conclusion.recommendation}</p>
                <p>
                  2. По уровню знаний оцениваем его на уровень{" "}
                  {cachedData.report.conclusion.assessed_level}
                </p>
                <p>3. {cachedData.report.conclusion.summary}</p>
              </div>

              <h3 className="text-base font-bold pt-2">
                5. Рекомендации для кандидата
              </h3>
              {cachedData.report.recommendations_for_candidate.length >
              0 ? (
                <ul className="pl-4 list-disc list-inside space-y-1">
                  {cachedData.report.recommendations_for_candidate.map(
                    (rec: string, i: number) => (
                      <li key={i}>{rec}</li>
                    )
                  )}
                </ul>
              ) : (
                <p className="pl-4 text-gray-500 italic">
                  Рекомендации не сгенерированы.
                </p>
              )}
            </div>
          </div>
        )}
      </>
    </div>
  );
}