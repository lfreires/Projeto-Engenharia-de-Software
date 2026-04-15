import React from "react";
import { DocAISidebar } from "./components/DocAISidebar";
import { ChatArea } from "./components/ChatArea";

export default function App() {
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        backgroundColor: "#f8f9fc",
      }}
    >
      {/* Fixed sidebar */}
      <DocAISidebar />

      {/* Chat main area */}
      <ChatArea />
    </div>
  );
}
