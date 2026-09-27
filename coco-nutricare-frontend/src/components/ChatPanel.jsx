import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { getMessages, sendMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { fmtDateTime } from "../utils";
import { ErrorText } from "./ui";

const POLL_MS = 4000;

/** Consultation chat. Polls the backend every 4 s for new messages. */
export default function ChatPanel({ consultation }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const lastId = useRef(0);
  const bottom = useRef(null);
  const closed = ["completed", "cancelled"].includes(consultation.status);

  useEffect(() => {
    lastId.current = 0;
    setMessages([]);
    let alive = true;
    const poll = async () => {
      try {
        const fresh = await getMessages(consultation.id, lastId.current);
        if (alive && fresh.length) {
          lastId.current = fresh[fresh.length - 1].id;
          setMessages((m) => [...m, ...fresh]);
        }
      } catch (e) {
        if (alive) setError(e.message);
      }
    };
    poll();
    const t = setInterval(poll, POLL_MS);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [consultation.id]);

  useEffect(() => bottom.current?.scrollIntoView({ block: "nearest" }), [messages]);

  const send = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    try {
      const m = await sendMessage(consultation.id, text);
      lastId.current = Math.max(lastId.current, m.id);
      setMessages((prev) => [...prev, m]);
      setText("");
      setError("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card flex h-[28rem] flex-col p-0">
      <div className="border-b border-coco-line px-5 py-3">
        <p className="font-semibold text-white">
          {user.id === consultation.doctor_id ? consultation.patient_name : consultation.doctor_name}
        </p>
        <p className="text-xs text-coco-muted">{consultation.reason}</p>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
        {messages.length === 0 && <p className="text-center text-sm text-coco-muted">No messages yet. Say hello.</p>}
        {messages.map((m) => {
          const mine = m.sender_id === user.id;
          return (
            <div key={m.id} className={`flex ${mine ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${mine ? "bg-coco-green text-white" : "bg-white/10 text-slate-100"}`}>
                <p>{m.text}</p>
                <p className="mt-1 text-[10px] opacity-70">{fmtDateTime(m.created_at)}</p>
              </div>
            </div>
          );
        })}
        <div ref={bottom} />
      </div>
      <div className="border-t border-coco-line p-3">
        <ErrorText error={error} />
        {closed ? (
          <p className="text-center text-sm text-coco-muted">This consultation is closed.</p>
        ) : (
          <form onSubmit={send} className="flex gap-2">
            <input className="input" placeholder="Write a message" value={text} onChange={(e) => setText(e.target.value)} />
            <button className="btn-green" aria-label="Send"><Send className="h-4 w-4" /></button>
          </form>
        )}
      </div>
    </div>
  );
}
