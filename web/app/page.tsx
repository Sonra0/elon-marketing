"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getJwt } from "../lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace(getJwt() ? "/dashboard" : "/login");
  }, [router]);
  return null;
}
