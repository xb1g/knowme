import { NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";
import path from "path";

export async function GET() {
  const jsonPath = path.join(process.cwd(), "..", "repo_mesh", "output", "latest_profile.json");

  if (!existsSync(jsonPath)) {
    return NextResponse.json({ error: "No mesh output found. Run the pipeline first." }, { status: 404 });
  }

  const data = JSON.parse(readFileSync(jsonPath, "utf-8"));
  return NextResponse.json(data);
}
