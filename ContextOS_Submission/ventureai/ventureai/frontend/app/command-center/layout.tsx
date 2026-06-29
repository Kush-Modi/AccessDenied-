import DashboardShell from "@/components/DashboardShell";

export default function CommandCenterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardShell breadcrumbs={[{ label: "Command Center", href: "/command-center" }]}>
      {children}
    </DashboardShell>
  );
}
