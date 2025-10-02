import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Brain, FileText, Video } from "lucide-react";
import InterviewPreparation from "./InterviewPreparation";
import InterviewResults from "./InterviewResults";
import { toast } from "./ui/use-toast";

interface DashboardProps {
  onLogout: () => void;
}

interface MatchingItem {
  criterion: string;
  match: string;
  comment: string;
}

interface Conclusion {
  summary: string;
  recommendations: string;
  interview_topics: string[];
  values_assessment: string;
}

interface Report {
  first_name: string | null;
  last_name: string | null;
  matching_table: MatchingItem[];
  candidate_profile: string;
  conclusion: Conclusion;
}

interface PreparationAnalysisResponse {
  message: string;
  success: boolean;
  report: Report;
}

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

interface CacheData {
  preparation?: PreparationAnalysisResponse;
  results?: ResultsAnalysisResponse;
}

interface LoadingStatus {
  preparation: boolean;
  results: boolean;
}

interface TaskStatusResponse {
  status: "processing" | "completed" | "failed";
  result?: ResultsAnalysisResponse;
  error?: string;
}

export default function Dashboard({ onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState("preparation");
  const [cache, setCache] = useState<CacheData>({});
  const [loadingStatus, setLoadingStatus] = useState<LoadingStatus>({
    preparation: false,
    results: false,
  });
  const [resultsTaskId, setResultsTaskId] = useState<string | null>(null);
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const updateCache = (tab: "preparation" | "results", data: any) => {
    setCache((prevCache) => ({
      ...prevCache,
      [tab]: data,
    }));
  };

  const setLoading = (tab: "preparation" | "results", status: boolean) => {
    setLoadingStatus((prevStatus) => ({
      ...prevStatus,
      [tab]: status,
    }));
  };

  useEffect(() => {
    // Не запускаем опрос, если нет ID задачи или процесс не активен
    if (!resultsTaskId || !loadingStatus.results) {
      return;
    }

    const intervalId = setInterval(async () => {
      try {
        // ИСПРАВЛЕНИЕ №1: Правильный URL для проверки статуса
        const res = await fetch(`${API_BASE_URL}/api/results/status/${resultsTaskId}`);

        if (!res.ok) {
          throw new Error(`Ошибка при проверке статуса: ${res.statusText}`);
        }

        const data = await res.json();

        // ИСПРАВЛЕНИЕ №2: Статус от RQ - 'finished', а не 'completed'
        if (data.status === "finished") {
          clearInterval(intervalId);
          setLoading("results", false);
          setResultsTaskId(null);
          if (data.result) {
            // В data.result лежит полный отчет от API
            updateCache("results", data.result);
            toast({
              title: "Успех",
              description: "Анализ видео успешно завершен.",
            });
          } else {
            throw new Error("Анализ завершен, но результат пустой.");
          }
        } else if (data.status === "failed") {
          clearInterval(intervalId);
          setLoading("results", false);
          setResultsTaskId(null);
          toast({
            title: "Ошибка анализа",
            description: data.error || "Произошла неизвестная ошибка в воркере.",
            variant: "destructive",
          });
        }
        // Если статус 'queued' или 'started', ничего не делаем и ждем следующей проверки
      } catch (error: any) {
        clearInterval(intervalId);
        setLoading("results", false);
        setResultsTaskId(null);
        toast({
          title: "Ошибка сети",
          description: `Не удалось получить статус задачи: ${error.message}`,
          variant: "destructive",
        });
      }
    }, 7000); // Опрос каждые 7 секунд

    // Эта функция очистки выполнится, если компонент будет размонтирован
    return () => clearInterval(intervalId);
  }, [resultsTaskId, loadingStatus.results, API_BASE_URL]);

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <header className="border-b bg-card/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              InterviewAI
            </h1>
          </div>
          <Button variant="ghost" size="sm" onClick={onLogout}>
            Back to Home
          </Button>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            Interview Analysis Platform
          </h2>
          <p className="text-muted-foreground">
            Prepare for interviews and analyze candidate performance with
            AI-powered insights
          </p>
        </div>
        <Card className="shadow-elegant bg-gradient-card border-0">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="w-full"
          >
            <CardHeader>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger
                  value="preparation"
                  className="flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>Interview Preparation</span>
                </TabsTrigger>
                <TabsTrigger
                  value="results"
                  className="flex items-center space-x-2"
                >
                  <Video className="w-4 h-4" />
                  <span>Interview Results</span>
                </TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent>
              <TabsContent value="preparation" className="mt-0">
                <InterviewPreparation
                  cachedData={cache.preparation}
                  updateCache={(data) => updateCache("preparation", data)}
                  isLoading={loadingStatus.preparation}
                  setIsLoading={(status) => setLoading("preparation", status)}
                />
              </TabsContent>
              <TabsContent value="results" className="mt-0">
                <InterviewResults
                  cachedData={cache.results}
                  updateCache={(data) => updateCache("results", data)}
                  isProcessing={loadingStatus.results}
                  setIsProcessing={(status) => setLoading("results", status)}
                  startAnalysisTask={setResultsTaskId}
                />
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </main>
    </div>
  );
}