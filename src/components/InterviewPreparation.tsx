// Файл: src/components/InterviewPreparation.tsx

import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Table, TableBody, TableCell, TableHeader, TableHead, TableRow } from './ui/table';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import { toast } from './ui/use-toast';
import { Loader2 } from 'lucide-react';

// 1. ОБНОВЛЕНЫ ТИПЫ ДАННЫХ
interface InterviewTopic {
  topic: string;
  questions: string[];
}

interface MatchingItem {
  criterion: string;
  match: string;
  comment: string;
}

interface Conclusion {
  summary: string;
  recommendations: string;
  interview_topics: InterviewTopic[]; // <-- ИЗМЕНЕНИЕ
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
  const [profile, setProfile] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setCvFile(event.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!cvFile || !profile) {
      toast({
        title: "Ошибка",
        description: "Пожалуйста, загрузите резюме и заполните профиль кандидата.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setAnalysisResponse(null);

    const formData = new FormData();
    formData.append('cv_file', cvFile);
    formData.append('profile', profile);

    try {
      const response = await fetch('http://localhost:8000/api/prep/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Произошла неизвестная ошибка');
      }

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

    const addTextBlock = (title: string, content: string) => {
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
      const splitText = doc.splitTextToSize(content, 180);
      doc.text(splitText, 14, lastY);
      lastY += splitText.length * 5 + 5;
    };

    addTextBlock("Общий вывод", report.conclusion.summary);
    addTextBlock("Рекомендации по развитию", report.conclusion.recommendations);
    
    // 3. ОБНОВЛЕНА ЛОГИКА ГЕНЕРАЦИИ PDF ДЛЯ ТЕМ И ВОПРОСОВ
    if (lastY > 260) {
      doc.addPage();
      lastY = 20;
    }
    doc.setFont('Roboto', 'bold');
    doc.setFontSize(14);
    doc.text("Темы для технического интервью", 14, lastY);
    lastY += 7;

    report.conclusion.interview_topics.forEach(topicItem => {
      if (lastY > 270) {
        doc.addPage();
        lastY = 20;
      }
      doc.setFont('Roboto', 'bold');
      doc.setFontSize(10);
      const splitTopic = doc.splitTextToSize(topicItem.topic, 180);
      doc.text(splitTopic, 14, lastY);
      lastY += splitTopic.length * 5;

      doc.setFont('Roboto', 'normal');
      topicItem.questions.forEach(question => {
        if (lastY > 275) {
          doc.addPage();
          lastY = 20;
        }
        const splitQuestion = doc.splitTextToSize(`- ${question}`, 175);
        doc.text(splitQuestion, 18, lastY);
        lastY += splitQuestion.length * 5;
      });
      lastY += 4;
    });

    addTextBlock("Оценка соответствия ценностям", report.conclusion.values_assessment);

    doc.save("Отчет_по_кандидату.pdf");
  };


  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Подготовка к интервью</h1>
      <Card>
        <CardHeader>
          <CardTitle>Предварительная оценка кандидата</CardTitle>
          <CardDescription>Загрузите резюме и фидбэк рекрутера (опционально) для генерации оценки и плана интервью.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="cv-file">Резюме (.txt, .pdf, .docx)</Label>
            <Input id="cv-file" type="file" onChange={handleFileChange} accept=".txt,.pdf,.docx" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="profile">Фидбэк рекрутера</Label>
            <Textarea
              id="profile"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              placeholder="Вставьте сюда текст..."
              rows={10}
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

            {/* 2. ОБНОВЛЕНА ЛОГИКА ОТОБРАЖЕНИЯ ТЕМ И ВОПРОСОВ */}
            <h3 className="font-bold text-lg mt-4 mb-2">Темы для технического интервью</h3>
            <div className="space-y-3">
              {analysisResponse.report.conclusion.interview_topics.map((topicItem, index) => (
                <div key={index}>
                  <h4 className="font-semibold">{topicItem.topic}</h4>
                  <ul className="list-disc list-inside text-sm space-y-1 mt-1">
                    {topicItem.questions.map((question, qIndex) => (
                      <li key={qIndex}>{question}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            <h3 className="font-bold text-lg mt-4 mb-2">Соответствие ценностям компании</h3>
            <p className="text-sm">{analysisResponse.report.conclusion.values_assessment}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InterviewPreparation;