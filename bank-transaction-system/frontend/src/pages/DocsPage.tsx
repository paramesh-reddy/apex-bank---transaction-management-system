import React from 'react';
import { ExternalLink, Database, ShieldCheck, Code2, Server } from 'lucide-react';

export const DocsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">API Documentation &amp; Architecture Specs</h1>
        <p className="text-xs text-slate-500 mt-1">
          Full-Stack Developer Assessment specifications, transaction atomicity guarantees, and API endpoints.
        </p>
      </div>

      <div className="p-5 rounded-2xl bg-emerald-950 text-white border border-emerald-800 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold">FastAPI Interactive Swagger Documentation</h2>
          <p className="text-xs text-emerald-200 mt-1">
            Explore and test live REST endpoints directly with interactive OpenAPI schema validation.
          </p>
        </div>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-colors shadow-sm shrink-0"
        >
          Open Swagger UI <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-600" /> Atomicity &amp; Pessimistic Locking
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every transaction runs inside a dedicated SQLAlchemy session. Balance verification and balance updates are protected with <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">SELECT ... FOR UPDATE</code>. If any validation or unique constraint check fails, the session is rolled back completely.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Code2 className="w-4 h-4 text-blue-600" /> Arbitrary-Precision Financial Math
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Floating-point arithmetic is strictly prohibited in financial backend services. All calculations use Python&apos;s <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">Decimal</code> and PostgreSQL <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">NUMERIC(18,2)</code> to eliminate round-off anomalies.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Server className="w-4 h-4 text-purple-600" /> Deadlock Prevention in Transfers
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Transfers sort sender and receiver UUIDs deterministically before acquiring row locks. This ensures all concurrent operations lock resources in identical order, completely preventing database deadlocks.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Database className="w-4 h-4 text-teal-600" /> Database-Level Immutability
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            In addition to omitting PUT, PATCH, and DELETE endpoints from the REST API, a PostgreSQL <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">BEFORE UPDATE OR DELETE</code> trigger raises an exception if direct SQL mutation is attempted on the transactions table.
          </p>
        </div>
      </div>
    </div>
  );
};
