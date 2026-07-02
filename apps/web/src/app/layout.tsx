import type { Metadata } from "next";
import { productName, productTagline } from "@audira/design-tokens";

import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: productName,
  description: productTagline,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
