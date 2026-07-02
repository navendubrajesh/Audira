export default function StudioLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="studio-root h-screen overflow-hidden">{children}</div>;
}
