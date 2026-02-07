"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { fetchDashboard, fetchDeals } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

const CHART_COLORS = {
  teal: "#133437",
  gold: "#B4A78B",
  sand: "#D8DAD3",
  olive: "#3D4D47",
  beige: "#DFDBD1",
  warmGold: "#96856C",
};

function SummaryCard({
  label,
  value,
  onClick,
}: {
  label: string;
  value: number;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="card text-left hover:shadow-soft transition-shadow cursor-pointer w-full"
    >
      <p className="text-sm font-ui text-text-secondary mb-2">{label}</p>
      <p className="text-3xl font-heading font-semibold text-teal-900">{value}</p>
    </button>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });
  const { data: recentDeals } = useQuery({
    queryKey: ["deals"],
    queryFn: () => fetchDeals(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-muted font-ui">Loading dashboard...</p>
      </div>
    );
  }

  const occupancyData = dashboard
    ? [
        { name: "Available", value: dashboard.unit_occupancy.available },
        { name: "Reserved", value: dashboard.unit_occupancy.reserved },
        { name: "Occupied", value: dashboard.unit_occupancy.occupied },
      ]
    : [];

  const dealStatusData = dashboard
    ? [
        { name: "In Progress", value: dashboard.deal_status_chart.in_progress },
        { name: "Invoice Requested", value: dashboard.deal_status_chart.invoice_requested },
        { name: "Completed", value: dashboard.deal_status_chart.completed },
      ]
    : [];

  const occupancyColors = [CHART_COLORS.teal, CHART_COLORS.gold, CHART_COLORS.olive];
  const dealColors = [CHART_COLORS.teal, CHART_COLORS.warmGold, CHART_COLORS.sand];

  const inProgressDeals = (recentDeals || [])
    .filter((d: any) => !["COMPLETED", "CANCELLED"].includes(d.status))
    .slice(0, 5);

  return (
    <div>
      <h2 className="text-[28px] mb-8">Dashboard</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <SummaryCard
          label="Deals in Progress"
          value={dashboard?.deals_in_progress ?? 0}
          onClick={() => router.push("/deals?status=IN_PROGRESS")}
        />
        <SummaryCard
          label="Deals Blocked"
          value={dashboard?.deals_blocked ?? 0}
          onClick={() => router.push("/deals?blocked=true")}
        />
        <SummaryCard
          label="Awaiting Action"
          value={dashboard?.deals_awaiting_action ?? 0}
          onClick={() => router.push("/deals?status=INVOICE_REQUESTED")}
        />
        <SummaryCard
          label="Completed"
          value={dashboard?.deals_completed ?? 0}
          onClick={() => router.push("/deals?status=COMPLETED")}
        />
      </div>

      {/* Donut Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Unit Occupancy
          </h4>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={occupancyData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                stroke="none"
              >
                {occupancyData.map((_, i) => (
                  <Cell key={i} fill={occupancyColors[i]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                verticalAlign="bottom"
                iconType="circle"
                formatter={(value) => (
                  <span className="text-sm font-ui text-text-secondary">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
            Deal Status
          </h4>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={dealStatusData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                stroke="none"
              >
                {dealStatusData.map((_, i) => (
                  <Cell key={i} fill={dealColors[i]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                verticalAlign="bottom"
                iconType="circle"
                formatter={(value) => (
                  <span className="text-sm font-ui text-text-secondary">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Deals */}
      <div className="card">
        <h4 className="text-lg font-heading font-semibold text-teal-900 mb-4">
          Active Deals
        </h4>
        {inProgressDeals.length === 0 ? (
          <p className="text-sm text-text-muted font-ui">No active deals.</p>
        ) : (
          <div className="space-y-3">
            {inProgressDeals.map((deal: any) => (
              <button
                key={deal.id}
                onClick={() => router.push(`/deals/${deal.id}`)}
                className="w-full flex items-center justify-between p-4 rounded-input border border-line-soft
                           hover:bg-neutral-softWhite transition-colors text-left"
              >
                <div>
                  <p className="font-ui font-medium text-sm text-teal-900">
                    {deal.deal_code}
                  </p>
                  <p className="text-xs text-text-secondary mt-1">
                    {deal.tenant?.full_name} — Unit {deal.unit?.unit_code}
                  </p>
                </div>
                <div className="text-right">
                  <span className="badge">{deal.status.replace(/_/g, " ")}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
