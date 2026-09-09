type ProxyContext = {
  params: Promise<{ path: string[] }>;
};

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

async function proxyRequest(request: Request, context: ProxyContext) {
  const { path } = await context.params;
  const configuredBase = process.env.BACKEND_API_URL || "http://127.0.0.1:8000";
  const target = new URL(configuredBase);
  const basePath = target.pathname.replace(/\/$/, "");
  target.pathname = `${basePath}/${path
    .map((segment) => encodeURIComponent(segment))
    .join("/")}`;
  if (["/api/tickets", "/incidents", "/alerts"].includes(target.pathname)) {
    target.pathname += "/";
  }
  target.search = new URL(request.url).search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  headers.delete("connection");
  headers.delete("accept-encoding");

  const hasBody = request.method !== "GET" && request.method !== "HEAD";

  try {
    const backendResponse = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      cache: "no-store",
      redirect: "follow",
    });

    const responseHeaders = new Headers();
    const contentType = backendResponse.headers.get("content-type");
    if (contentType) responseHeaders.set("content-type", contentType);

    return new Response(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      {
        detail:
          "ارتباط سرور فرانت با بک‌اند برقرار نشد. تنظیم BACKEND_API_URL و وضعیت سرویس بک‌اند را بررسی کنید.",
      },
      { status: 502 },
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;
export const HEAD = proxyRequest;
