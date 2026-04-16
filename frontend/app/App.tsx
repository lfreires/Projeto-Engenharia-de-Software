import React from "react";
import { DocAISidebar } from "@/views/layouts/DocAISidebar";
import { ChatArea } from "@/views/components/ChatArea";

export default function App() {
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif", backgroundColor: "#f8f9fc" }}
    >
      <DocAISidebar />
      <ChatArea />
    </div>
  );
}
