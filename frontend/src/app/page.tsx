import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search, Plane } from "lucide-react";

// Mock data for initial development
const MOCK_REPORTS = [
  {
    report_id: "1",
    facility_id: "KORD",
    status_type: "RUNWAY_CLOSURE",
    raw_notam_text: "RWY 10C/28C CLSD WEF 2312231400",
    timestamp_utc: "2025-12-23T14:30:00Z",
  },
  {
    report_id: "2",
    facility_id: "KJFK",
    status_type: "NORMAL_OPS",
    raw_notam_text: "ALL RWY OPEN AND OPERATIONAL. NO SIG WX.",
    timestamp_utc: "2025-12-23T14:15:00Z",
  },
  {
    report_id: "3",
    facility_id: "EGLL",
    status_type: "DEICING",
    raw_notam_text: "DEICING IN PROGRESS. EXPECT 20 MIN DELAY.",
    timestamp_utc: "2025-12-23T14:45:00Z",
  },
  {
    report_id: "4",
    facility_id: "EDDF",
    status_type: "CAUTION",
    raw_notam_text: "TWY BRAVO REDUCED VISIBILITY.",
    timestamp_utc: "2025-12-23T13:30:00Z",
  },
];

const getStatusColor = (type: string) => {
  switch (type) {
    case "RUNWAY_CLOSURE":
      return "bg-[hsl(var(--status-closed))] hover:bg-[hsl(var(--status-closed))]/90 text-white";
    case "DEICING":
    case "CAUTION":
      return "bg-[hsl(var(--status-caution))] hover:bg-[hsl(var(--status-caution))]/90 text-black";
    case "NORMAL_OPS":
      return "bg-[hsl(var(--status-normal))] hover:bg-[hsl(var(--status-normal))]/90 text-white";
    default:
      return "bg-secondary text-secondary-foreground";
  }
};

export default function Dashboard() {
  // In a real implementation, we would fetch data here (Server Component)
  const reports = MOCK_REPORTS;

  return (
    <div className="min-h-screen bg-atc-background text-foreground p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
              <Plane className="h-8 w-8 text-primary" />
              FLOS Controller Dashboard
            </h1>
            <p className="text-atc-muted">
              Live Facility Status Monitoring • UTC {new Date().toISOString().slice(11, 16)}Z
            </p>
          </div>
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search facility (e.g., KORD, EGLL)..."
              className="pl-10 bg-atc-card border-slate-700 text-white placeholder:text-slate-500 focus-visible:ring-primary"
            />
          </div>
        </header>

        {/* Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report) => (
            <Card key={report.report_id} className="bg-atc-card border-slate-700 hover:border-slate-600 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-2xl font-mono text-white">
                  {report.facility_id}
                </CardTitle>
                <Badge className={getStatusColor(report.status_type)}>
                  {report.status_type.replace(/_/g, " ")}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-atc-muted uppercase tracking-wider">
                    Latest Report
                  </span>
                  <p className="text-sm font-mono text-slate-300 leading-relaxed break-words atc-data-block bg-slate-900/50 p-3 rounded border border-slate-800">
                    {report.raw_notam_text}
                  </p>
                </div>
                <div className="flex items-center justify-between text-xs text-atc-muted pt-2 border-t border-slate-700/50">
                  <span>ID: {report.report_id}</span>
                  <span className="font-mono">
                    {new Date(report.timestamp_utc).toLocaleTimeString("en-GB", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}Z
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
