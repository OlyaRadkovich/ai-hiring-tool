import { useState } from "react";
import LandingPage from "@/components/LandingPage";
import Dashboard from "@/components/Dashboard";

const Index = () => {
  const [currentView, setCurrentView] = useState<"landing" | "dashboard">("landing");

  const handleGetStarted = () => {
    setCurrentView("dashboard");
  };

  const handleLogout = () => {
    setCurrentView("landing");
  };

  if (currentView === "dashboard") {
    return <Dashboard onLogout={handleLogout} />;
  }

  return <LandingPage onGetStarted={handleGetStarted} />;
};

export default Index;
