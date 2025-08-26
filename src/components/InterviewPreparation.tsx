import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from './ui/table';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import { toast } from './ui/use-toast';
import { Loader2 } from 'lucide-react';

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

interface AnalysisResponse {
  message: string;
  success: boolean;
  report: Report;
}

const InterviewPreparation: React.FC = () => {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [feedbackFile, setFeedbackFile] = useState<File | null>(null);
  const [requirementsLink, setRequirementsLink] = useState('https://docs.google.com/spreadsheets/d/1rtLBPqaJGkcZzUWDX01P5VI01bBGQ1B8H5g_S8PhXL0/edit?usp=sharing');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse | null>(null);

  const handleCvFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setCvFile(event.target.files[0]);
    }
  };

  const handleFeedbackFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFeedbackFile(event.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    const defaultLink = 'https://docs.google.com/spreadsheets/d/1rtLBPqaJGkcZzUWDX01P5VI01bBGQ1B8H5g_S8PhXL0/edit?usp=sharing';

    if (requirementsLink === defaultLink || requirementsLink.trim() === '') {
      toast({
        title: "Ошибка",
        description: "Пожалуйста, укажите корректную ссылку на требования к кандидату.",
        variant: "destructive",
      });
      return;
    }

    if (!cvFile || !feedbackFile) {
      toast({
        title: "Ошибка",
        description: "Пожалуйста, загрузите резюме и фидбэк от рекрутера.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setAnalysisResponse(null);

    const formData = new FormData();
    formData.append('cv_file', cvFile);
    formData.append('feedback_file', feedbackFile);
    formData.append('requirements_link', requirementsLink);

    try {
      const response = await fetch('http://localhost:8000/api/prep/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Сначала пытаемся прочитать ошибку как JSON
        try {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Ошибка сервера: ${response.status}`);
        } catch {
            // Если тело ответа не JSON, показываем общую ошибку
            throw new Error(`Ошибка сервера: ${response.status}`);
        }
      }

      const data = await response.json();
      setAnalysisResponse(data);
      toast({
        title: "Успех",
        description: "Анализ успешно завершен.",
      });
    } catch (error: any) {
      toast({
        title: "Ошибка анализа",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPdf = async () => {
    if (!analysisResponse?.report) {
      alert("Нет данных для генерации отчета.");
      return;
    }
    const { report } = analysisResponse;
    const doc = new jsPDF();

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
    doc.text("Предварительная оценка кандидата", 14, 20);

    doc.setFontSize(14);
    doc.text(`${report.first_name || ''} ${report.last_name || ''}`, 14, 30);

    const profileY = 30 + 10;
    doc.setFontSize(12);
    doc.text(`Предполагаемый профиль: ${report.candidate_profile}`, 14, profileY);

    const tableTitleY = profileY + 15;
    doc.setFont('Roboto', 'bold');
    doc.setFontSize(14);
    doc.text("Соответствие ключевым критериям", 14, tableTitleY);

    autoTable(doc, {
      startY: tableTitleY + 5,
      head: [['Критерий', 'Соответствие', 'Пояснение']],
      body: report.matching_table.map(item => {
        const capitalizedCriterion = item.criterion.charAt(0).toUpperCase() + item.criterion.slice(1);
        return [capitalizedCriterion, item.match, item.comment];
      }),
      theme: 'grid',
      styles: { font: 'Roboto', fontSize: 10 },
      headStyles: { fillColor: [41, 128, 185], fontStyle: 'bold' },
      columnStyles: {
        0: { cellWidth: 55 },
        1: { cellWidth: 35 },
        2: { cellWidth: 'auto' }
      },
    });

    let lastY = (doc as any).lastAutoTable.finalY + 15;

    const addTextBlock = (title: string, content: string | string[]) => {
      if (lastY > 260) {
          doc.addPage();
          lastY = 20;
      }
      doc.setFont('Roboto', 'bold');
      doc.setFontSize(14);
      doc.text(title, 14, lastY);
      lastY += 7;
      doc.setFont('Roboto', 'normal');
      doc.setFontSize(10);
      const textToSplit = Array.isArray(content) ? content.join('\n') : content;
      const splitText = doc.splitTextToSize(textToSplit, 180);
      doc.text(splitText, 14, lastY);
      lastY += splitText.length * 5 + 5;
    };

    addTextBlock("Общий вывод", report.conclusion.summary);
    addTextBlock("Рекомендации по развитию", report.conclusion.recommendations);
    addTextBlock("Темы для технического интервью", report.conclusion.interview_topics);
    addTextBlock("Оценка соответствия ценностям", report.conclusion.values_assessment);

    doc.save("Отчет_по_кандидату.pdf");
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Подготовка к интервью</h1>
      <Card>
        <CardHeader>
          <CardTitle>Оценка кандидата</CardTitle>
          <CardDescription>
            Загрузите резюме и фидбек от рекрутера (в форматах .txt, .pdf или .docx) для генерации предварительной оценки кандидата. При необходимости измените ссылку на требования к кандидату.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="cv-file">Резюме (.txt, .pdf, .docx)</Label>
            <Input id="cv-file" type="file" onChange={handleCvFileChange} accept=".txt,.pdf,.docx" />
          </div>
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="feedback-file">Фидбек от рекрутера</Label>
            <Input id="feedback-file" type="file" onChange={handleFeedbackFileChange} accept=".txt,.pdf,.docx" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="requirements">Требования к кандидату</Label>
            <Input
              id="requirements"
              value={requirementsLink}
              onChange={(e) => setRequirementsLink(e.target.value)}
              placeholder="Вставьте ссылку на Google Таблицу..."
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? 'Анализ...' : 'Начать анализ'}
          </Button>
        </CardFooter>
      </Card>

      {analysisResponse && (
        <Card className="mt-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Результаты анализа</CardTitle>
              <Button onClick={handleExportPdf} variant="outline">Экспорт в PDF</Button>
            </div>
            <CardDescription>
              {`Профиль: ${analysisResponse.report.candidate_profile} (${analysisResponse.report.first_name || ''} ${analysisResponse.report.last_name || ''})`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <h3 className="font-bold text-lg mb-2">Соответствие ключевым критериям</h3>
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40%]">Критерий</TableHead>
                    <TableHead className="w-[15%]">Соответствие</TableHead>
                    <TableHead>Пояснение</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analysisResponse.report.matching_table.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>{item.criterion}</TableCell>
                      <TableCell>{item.match}</TableCell>
                      <TableCell>{item.comment}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <h3 className="font-bold text-lg mt-4 mb-2">Общий вывод</h3>
            <p className="text-sm">{analysisResponse.report.conclusion.summary}</p>

            <h3 className="font-bold text-lg mt-4 mb-2">Рекомендации по развитию</h3>
            <p className="text-sm">{analysisResponse.report.conclusion.recommendations}</p>

            <h3 className="font-bold text-lg mt-4 mb-2">Темы для технического интервью</h3>
            <ul className="list-disc list-inside text-sm space-y-1">
              {analysisResponse.report.conclusion.interview_topics.map((topic, index) => (
                <li key={index}>{topic}</li>
              ))}
            </ul>

            <h3 className="font-bold text-lg mt-4 mb-2">Соответствие ценностям компании</h3>
            <p className="text-sm">{analysisResponse.report.conclusion.values_assessment}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InterviewPreparation;