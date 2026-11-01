"""
RubricWard API Gateway — FastAPI Application Entrypoint.
Mounts all 12 Commercial Payer TiC MRF, Medicare MPFS RVU/GPCI, ERISA 29 CFR 2560.503-1 Appeal,
and Federal No Surprises Act (NSA 45 CFR 149.510) IDR Arbitration Microservices,
the 6-File OpenXML .ZIP Claim/IDR Package Compiler, and the Remote Streamable-HTTP MCP Server.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from api_gateway.core.config import settings
from api_gateway.routers.precon_endpoints import router as precon_router
from api_gateway.routers.camber_autopilot import router as camber_autopilot_router
from api_gateway.routers.billing_webhook import router as billing_router
from api_gateway.routers.mcp import router as mcp_router

ROOT_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Stateless B2B Healthcare Commercial Payer Rate-Transparency (CMS TiC 45 CFR 147.212 MRF), "
        "Medicare Physician Fee Schedule (MPFS) RVU & GPCI Locality Calculator, Clinical Policy Bulletin (CPB) Shredder, "
        "CMS NCCI PTP/MUE Scrubber, Federal No Surprises Act (NSA 45 CFR 149.510) IDR Arbitration Brief Generator, "
        "ERISA 29 CFR 2560.503-1 Medical Necessity Appeal Drafter, HIPAA X12 835 Remittance Auditor, "
        "and 1-Click 6-File OpenXML (.DOCX + .XLSX) Claim & IDR Package Compiler API Gateway."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(precon_router, prefix=settings.API_V1_STR)
app.include_router(camber_autopilot_router, prefix=settings.API_V1_STR)
app.include_router(billing_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router)

if (ROOT_DIR / "lettings").exists():
    app.mount("/lettings", StaticFiles(directory=str(ROOT_DIR / "lettings"), html=True), name="lettings")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_path = ROOT_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return HTMLResponse("<h1>RubricWard Commercial Payer MRF, ERISA Appeal & NSA IDR API Gateway</h1>")


@app.get("/apis", include_in_schema=False)
@app.get("/apis.html", include_in_schema=False)
async def serve_apis():
    apis_path = ROOT_DIR / "apis.html"
    if apis_path.exists():
        return FileResponse(str(apis_path), media_type="text/html")
    return HTMLResponse("<h1>RubricWard API Catalog</h1>")


@app.get("/sitemap.xml", include_in_schema=False)
async def serve_sitemap():
    sitemap_path = ROOT_DIR / "sitemap.xml"
    if sitemap_path.exists():
        return FileResponse(str(sitemap_path), media_type="application/xml")
    return HTMLResponse("<urlset/>", media_type="application/xml")


@app.get("/robots.txt", include_in_schema=False)
async def serve_robots():
    robots_path = ROOT_DIR / "robots.txt"
    if robots_path.exists():
        return FileResponse(str(robots_path), media_type="text/plain")
    return HTMLResponse("User-agent: *\nAllow: /\nSitemap: https://rubricward.com/sitemap.xml\n", media_type="text/plain")


@app.get("/a4f8e2c91b7d3056e8a12f4c9d0b3e71.txt", include_in_schema=False)
async def serve_indexnow_key():
    return HTMLResponse("a4f8e2c91b7d3056e8a12f4c9d0b3e71", media_type="text/plain")


@app.get("/favicon.svg", include_in_schema=False)
@app.get("/lettings/favicon.svg", include_in_schema=False)
async def serve_favicon_svg():
    for candidate in (ROOT_DIR / "favicon.svg", ROOT_DIR / "lettings" / "favicon.svg"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/svg+xml")
    return HTMLResponse("", media_type="image/svg+xml")


@app.get("/bimi-logo.svg", include_in_schema=False)
@app.get("/lettings/bimi-logo.svg", include_in_schema=False)
async def serve_bimi_svg():
    for candidate in (ROOT_DIR / "bimi-logo.svg", ROOT_DIR / "lettings" / "bimi-logo.svg", ROOT_DIR / "favicon.svg"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/svg+xml")
    return HTMLResponse("", media_type="image/svg+xml")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/lettings/favicon.ico", include_in_schema=False)
async def serve_favicon_ico():
    for candidate in (ROOT_DIR / "favicon.ico", ROOT_DIR / "lettings" / "favicon.ico"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/x-icon")
    return await serve_favicon_svg()


@app.get("/favicon.png", include_in_schema=False)
@app.get("/lettings/favicon.png", include_in_schema=False)
async def serve_favicon_png():
    for candidate in (ROOT_DIR / "favicon.png", ROOT_DIR / "lettings" / "favicon.png"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/png")
    return await serve_favicon_svg()


@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
@app.get("/lettings/apple-touch-icon.png", include_in_schema=False)
async def serve_apple_touch_icon():
    for candidate in (ROOT_DIR / "apple-touch-icon.png", ROOT_DIR / "lettings" / "apple-touch-icon.png", ROOT_DIR / "favicon.png"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/png")
    return await serve_favicon_svg()


@app.get("/og-image.png", include_in_schema=False)
@app.get("/lettings/og-image.png", include_in_schema=False)
async def serve_og_image():
    for candidate in (ROOT_DIR / "og-image.png", ROOT_DIR / "lettings" / "og-image.png", ROOT_DIR / "apple-touch-icon.png"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/png")
    return await serve_favicon_svg()


@app.get("/site.webmanifest", include_in_schema=False)
@app.get("/lettings/site.webmanifest", include_in_schema=False)
async def serve_site_webmanifest():
    for candidate in (ROOT_DIR / "site.webmanifest", ROOT_DIR / "lettings" / "site.webmanifest"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="application/manifest+json")
    return HTMLResponse("{}", media_type="application/manifest+json")


@app.get("/favicon-{dims}.png", include_in_schema=False)
@app.get("/lettings/favicon-{dims}.png", include_in_schema=False)
async def serve_sized_favicon_png(dims: str):
    fname = f"favicon-{dims}.png"
    for candidate in (ROOT_DIR / fname, ROOT_DIR / "lettings" / fname, ROOT_DIR / "favicon.png"):
        if candidate.exists():
            return FileResponse(str(candidate), media_type="image/png")
    return await serve_favicon_svg()
