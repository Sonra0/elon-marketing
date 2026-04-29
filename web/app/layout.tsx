import "./globals.css";
import { Nav } from "../components/Nav";

export const metadata = { title: "Elon", description: "Brand marketing agent" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  );
}
