r"""
RubricWard Headless RapidAPI Studio Publisher (`D:\RubricWard\publish_rubricward_rapidapi.py`)
Publishes all 12 RubricWard Construction, 50-State DOT Bid-Tab & Prevailing-Wage APIs to the
dedicated `RubricWardSystems` RapidAPI account (`Entity ID: 12422060`):
  1. Creates each API project via `createApisFromRapidOas` pointing to `https://rubricward.com`
  2. Uploads its 500x500 PNG Symbol #07 logo, Markdown `longDescription`, `websiteUrl`, and sets `visibility: "PUBLIC"`
  3. Configures the Green Health Check badge (`upsertApiHealthcheck` -> `https://rubricward.com/v1/health`)
  4. Configures all 4 pricing plans (`BASIC $0`, `PRO $49`, `ULTRA $149` recommended, `MEGA $399`)
  5. Saves all 12 `apiId`s, `slugifiedName`s, `rapid_host`s, and `X-RapidAPI-Proxy-Secret`s to `D:\RubricWard\rapidapi_published_catalog.json` and `D:\RubricWard\.env`.
"""

import json
from pathlib import Path
import time
from typing import Any, Dict, List
import requests

from generate_rapidapi_kit import ASSETS_DIR, RUBRICWARD_RAPIDAPI_CATALOG, generate_all_kits

ROOT_DIR = Path(__file__).resolve().parent
SESSION_FILE = ROOT_DIR / "rapidapi_session.json"
PUBLISHED_OUT = ROOT_DIR / "rapidapi_published_catalog.json"
ENV_FILE = ROOT_DIR / ".env"
GQL_URL = "https://rapidapi.com/gateway/graphql"
BACKEND_URL = "https://api.rubricward.com"
ENTITY_ID = "12422060"
PROVIDER_NAME = "RubricWardSystems"

STUDIO_TITLES_60: Dict[str, str] = {
    "01": "CSI MasterFormat Spec & Submittal Shredder API",
    "02": "50-State DOT Historical Item Bid Tabulation API",
    "03": "Davis-Bacon 29 CFR 5 Prevailing Wage Calculator API",
    "04": "52-Portal Live State DOT & Public Works Lettings API",
    "05": "Build America Buy America BABA Material Auditor API",
    "06": "DOT DBE 49 CFR Part 26 Good Faith Effort Generator API",
    "07": "AIA G702 G703 Schedule of Values Pay App Generator API",
    "08": "Miller Act 40 USC 3131 Surety Bond Underwriter API",
    "09": "Construction RFI & AIA G701 Change Order Claim API",
    "10": "OSHA 1926 USACE EM 385-1-1 Safety AHA & EMR Auditor API",
    "11": "DOT Planholder Competitor Spread & MLOT Analyzer API",
    "12": "Subcontractor ITB Scope Sheet & AIA A401 Generator API",
}


def load_session() -> requests.Session:
    sess_data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    s = requests.Session()
    headers = dict(sess_data.get("headers") or {})
    headers["x-entity-id"] = ENTITY_ID
    headers["x-rapidapi-Rolling-Key"] = "true"
    headers.pop("content-type", None)
    s.headers.update(headers)

    csrf_resp = s.get("https://rapidapi.com/gateway/csrf", timeout=20)
    if csrf_resp.status_code == 200:
        tok = (csrf_resp.json() or {}).get("csrfToken")
        if tok:
            s.headers["csrf-token"] = tok
    return s


def gql(s: requests.Session, query: str, variables: Dict[str, Any] = None, op_name: str = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"query": query, "variables": variables or {}}
    if op_name:
        payload["operationName"] = op_name
    for attempt in range(3):
        try:
            r = s.post(GQL_URL, json=payload, timeout=30)
            try:
                return r.json()
            except Exception:
                return {"status_code": r.status_code, "raw": r.text[:400]}
        except requests.exceptions.RequestException as exc:
            if attempt == 2:
                return {"error": str(exc)}
            time.sleep(2.0 * (attempt + 1))
    return {}


def publish_all_12_apis() -> List[Dict[str, Any]]:
    generate_all_kits(base_url=BACKEND_URL)
    s = load_session()

    existing_res = gql(
        s,
        """
        query($ownerId: [ID!]!) {
          apis(where: { ownerId: $ownerId }, pagination: { first: 50 }) {
            nodes {
              id
              name
              slugifiedName
              visibility
            }
          }
        }
        """,
        {"ownerId": [ENTITY_ID]},
    )
    existing_nodes = (((existing_res.get("data") or {}).get("apis") or {}).get("nodes")) or []
    print(f"[RAPIDAPI STUDIO] Existing APIs on {PROVIDER_NAME} ({ENTITY_ID}): {len(existing_nodes)}")

    published_results: List[Dict[str, Any]] = []
    proxy_secrets: List[str] = []

    for api in RUBRICWARD_RAPIDAPI_CATALOG:
        num = api["num"]
        studio_title = STUDIO_TITLES_60[num]
        oas_path = ASSETS_DIR / f"rapidapi_api{num}_openapi.json"
        logo_path = ASSETS_DIR / f"api{num}_{api['slug'].replace('-', '_')}_logo.png"
        readme_path = ASSETS_DIR / f"rapidapi_api{num}_readme.md"
        readme_text = readme_path.read_text(encoding="utf-8")

        # Prepare clean OpenAPI file for RapidAPI Studio import (title <= 60 chars, no /v1/health path in import)
        oas_obj = json.loads(oas_path.read_text(encoding="utf-8"))
        paths_copy = dict(oas_obj.get("paths") or {})
        paths_copy.pop("/v1/health", None)
        clean_oas = {
            "openapi": "3.0.3",
            "info": {
                "title": studio_title,
                "version": "1.0.0",
                "x-category": "Business",
                "description": api["short_description"].encode("ascii", "ignore").decode("ascii"),
            },
            "servers": [{"url": BACKEND_URL}],
            "paths": paths_copy,
        }
        clean_oas_path = ASSETS_DIR / f"rapidapi_api{num}_studio_import.json"
        clean_oas_path.write_text(json.dumps(clean_oas, indent=2), encoding="utf-8")

        api_id = None
        for node in existing_nodes:
            if (node.get("name") or "").strip().lower() == studio_title.lower():
                api_id = node["id"]
                break

        if not api_id:
            create_ops = json.dumps(
                {
                    "operationName": "createApisFromRapidOas",
                    "variables": {"creations": [{"spec": None}]},
                    "query": """
                    mutation createApisFromRapidOas($creations: [ApiCreateFromRapidOasInput!]!) {
                      createApisFromRapidOas(creations: $creations) {
                        apiId
                        trackingId
                      }
                    }
                    """,
                }
            )
            with open(clean_oas_path, "rb") as spec_f:
                create_resp = s.post(
                    GQL_URL,
                    data={
                        "operations": create_ops,
                        "map": json.dumps({"0": ["variables.creations.0.spec"]}),
                    },
                    files={"0": (clean_oas_path.name, spec_f, "application/json")},
                    timeout=45,
                ).json()
            created_list = (create_resp.get("data") or {}).get("createApisFromRapidOas") or []
            if created_list:
                api_id = created_list[0].get("apiId")
                time.sleep(1.5)
            else:
                print(f"[!] Failed createApisFromRapidOas for API #{num}: {create_resp}")
                continue

        raw_info = gql(
            s,
            """
            query($id: ID!) {
              api(id: $id) {
                id
                name
                slugifiedName
                secret
                category
                visibility
                currentVersion {
                  id
                  name
                }
                billingPlans {
                  id
                  name
                  version {
                    id
                    billinglimits {
                      billingitem {
                        id
                      }
                    }
                  }
                }
              }
            }
            """,
            {"id": api_id},
        )
        info = (raw_info.get("data") or {}).get("api") or {}
        slug_name = info.get("slugifiedName") or api["slug"]
        secret = info.get("secret") or ""
        if secret and secret not in proxy_secrets:
            proxy_secrets.append(secret)

        # Update Logo, Long Description, Website URL & Visibility = PUBLIC
        operations = json.dumps(
            {
                "operationName": "UpdateApiMeta",
                "variables": {
                    "api": {
                        "id": api_id,
                        "category": api.get("category") or "Business",
                        "description": api["short_description"][:280],
                        "longDescription": readme_text,
                        "termsOfService": {"text": ""},
                        "websiteUrl": f"https://rubricward.com/apis.html#product-{api['slug']}",
                        "visibility": "PUBLIC",
                        "thumbnail": None,
                        "tags": [],
                        "config": {"generateSDK": False},
                    }
                },
                "query": """
                mutation UpdateApiMeta($api: ApiUpdateInput!) {
                  updateApi(api: $api) {
                    id
                    slugifiedName
                    visibility
                    thumbnail
                  }
                }
                """,
            }
        )
        with open(logo_path, "rb") as img_f:
            upd_resp = s.post(
                GQL_URL,
                data={
                    "operations": operations,
                    "map": json.dumps({"0": ["variables.api.thumbnail"]}),
                },
                files={"0": (logo_path.name, img_f, "image/png")},
                timeout=45,
            ).json()
        upd_node = (upd_resp.get("data") or {}).get("updateApi") or {}
        final_vis = upd_node.get("visibility") or "PUBLIC"

        # Configure 4 Pricing Plans (BASIC $0, PRO $49, ULTRA $149 recommended, MEGA $399)
        ver_id = (info.get("currentVersion") or {}).get("id")
        ver_name = (info.get("currentVersion") or {}).get("name") or "1.0.0"

        if ver_id:
            update_oas_ops = json.dumps(
                {
                    "operationName": "updateApisFromRapidOas",
                    "variables": {"updates": [{"apiVersionId": ver_id, "spec": None}]},
                    "query": """
                    mutation updateApisFromRapidOas($updates: [ApiUpdateFromRapidOasInput!]!) {
                      updateApisFromRapidOas(updates: $updates) {
                        apiId
                        trackingId
                      }
                    }
                    """,
                }
            )
            with open(clean_oas_path, "rb") as spec_f:
                s.post(
                    GQL_URL,
                    data={
                        "operations": update_oas_ops,
                        "map": json.dumps({"0": ["variables.updates.0.spec"]}),
                    },
                    files={"0": (clean_oas_path.name, spec_f, "application/json")},
                    timeout=45,
                )

        # Configure Health Check URL (must run after updateApisFromRapidOas)
        gql(
            s,
            """
            mutation($apiId: ID!, $healthCheckUrl: String!) {
              upsertApiHealthcheck(apiId: $apiId, healthCheckUrl: $healthCheckUrl)
            }
            """,
            {"apiId": api_id, "healthCheckUrl": f"{BACKEND_URL}/v1/health"},
        )
        bplans = info.get("billingPlans") or []
        if ver_id and bplans:
            item_id = bplans[0]["version"]["billinglimits"][0]["billingitem"]["id"]
            existing_plans = {p["name"]: p["id"] for p in bplans}
            basic_id = existing_plans.get("BASIC")
            if basic_id:
                basic_ext = {
                    "api": api_id,
                    "apiName": studio_title,
                    "apiVersion": ver_id,
                    "apiVersionName": ver_name,
                    "providerName": PROVIDER_NAME,
                    "billingPlanId": basic_id,
                    "isStudent": False,
                    "isPrivatePlan": False,
                    "legalAccountId": "",
                    "legalDocumentId": "",
                    "name": "BASIC",
                    "targetGroup": "",
                    "billingLimits": [
                        {
                            "amount": 10,
                            "item": item_id,
                            "limitType": "hard",
                            "overagePrice": 0,
                            "period": "MONTHLY",
                            "perusagePrice": 0,
                            "unlimited": False,
                        }
                    ],
                    "enableBillingFeatures": [],
                    "price": 0,
                    "type": "MONTHLY",
                    "shouldRequestApproval": False,
                    "requestApprovalQuestion": "",
                    "rateLimit": {"amount": 10, "enabled": True, "unit": 1, "unitName": "hour"},
                }
                gql(
                    s,
                    """
                    mutation UpdateBasic($ext: BillingPlanExtendedUpdateInput!) {
                      updateBillingPlanExtended(billingPlan: $ext) {
                        id
                        name
                      }
                    }
                    """,
                    {"ext": basic_ext},
                    "UpdateBasic",
                )

            for pname, price, quota, overage, is_rec in [
                ("PRO", 49, 200, 0.25, False),
                ("ULTRA", 149, 1000, 0.15, True),
                ("MEGA", 399, 4000, 0.10, False),
            ]:
                if pname in existing_plans:
                    continue
                c_input = {
                    "api": api_id,
                    "apiName": studio_title,
                    "apiVersion": ver_id,
                    "apiVersionName": ver_name,
                    "providerName": PROVIDER_NAME,
                    "isStudent": False,
                    "isPrivatePlan": False,
                    "legalAccountId": "",
                    "legalDocumentId": "",
                    "name": pname,
                    "targetGroup": "",
                    "billingLimits": [
                        {
                            "amount": quota,
                            "item": item_id,
                            "limitType": "soft",
                            "overagePrice": overage,
                            "period": "MONTHLY",
                            "perusagePrice": overage,
                            "unlimited": False,
                        }
                    ],
                    "enableBillingFeatures": [],
                    "price": price,
                    "type": "MONTHLY",
                    "shouldRequestApproval": False,
                    "requestApprovalQuestion": "",
                }
                r_create = gql(
                    s,
                    """
                    mutation createBillingPlan($input: BillingPlanCreateInput!) {
                      createBillingPlan(billingPlan: $input) {
                        id
                        name
                      }
                    }
                    """,
                    {"input": c_input},
                    "createBillingPlan",
                )
                new_pid = ((r_create.get("data") or {}).get("createBillingPlan") or {}).get("id")
                if is_rec and new_pid:
                    gql(
                        s,
                        """
                        mutation SetRec($input: BillingPlanMetadataUpdateInput!) {
                          updateBillingPlanMetadata(billingPlan: $input) {
                            id
                            recommended
                          }
                        }
                        """,
                        {
                            "input": {
                                "billingPlanId": new_pid,
                                "recommended": True,
                                "legalDocumentId": "",
                                "legalAccountId": "",
                            }
                        },
                        "SetRec",
                    )

        rapid_host = f"{slug_name}.p.rapidapi.com"
        hub_url = f"https://rapidapi.com/RubricWardSystems/api/{slug_name}"
        rec = {
            "num": num,
            "title": studio_title,
            "api_id": api_id,
            "slug": slug_name,
            "rapid_host": rapid_host,
            "hub_url": hub_url,
            "visibility": final_vis,
            "proxy_secret": secret,
            "route": api["route"],
            "method": api["method"],
        }
        published_results.append(rec)
        print(f"[PUBLISHED] API #{num}: {studio_title} -> {hub_url} ({final_vis})")

    PUBLISHED_OUT.write_text(json.dumps(published_results, indent=2), encoding="utf-8")

    if proxy_secrets and ENV_FILE.exists():
        env_txt = ENV_FILE.read_text(encoding="utf-8")
        joined_secrets = ",".join(proxy_secrets)
        if "RAPIDAPI_PROXY_SECRET=" in env_txt:
            lines = [
                f"RAPIDAPI_PROXY_SECRET={joined_secrets}" if ln.startswith("RAPIDAPI_PROXY_SECRET=") else ln
                for ln in env_txt.splitlines()
            ]
            ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            ENV_FILE.write_text(env_txt.rstrip() + f"\nRAPIDAPI_PROXY_SECRET={joined_secrets}\n", encoding="utf-8")

    return published_results


def verify_healthchecks() -> None:
    s = load_session()
    items = json.loads(PUBLISHED_OUT.read_text(encoding="utf-8"))
    for it in items:
        gql(
            s,
            "mutation($api: ApiUpdateInput!) { updateApi(api: $api) { id visibility } }",
            {"api": {"id": it["api_id"], "visibility": "PUBLIC"}},
        )
        gql(
            s,
            "mutation($apiId: ID!, $healthCheckUrl: String!) { upsertApiHealthcheck(apiId: $apiId, healthCheckUrl: $healthCheckUrl) }",
            {"apiId": it["api_id"], "healthCheckUrl": f"{BACKEND_URL}/v1/health"},
        )
    time.sleep(2.5)
    for it in items:
        r = gql(
            s,
            "query($id: ID!) { api(id: $id) { visibility apiHealthCheck { healthcheckStatus { status } } } }",
            {"id": it["api_id"]},
        )
        api_node = (r.get("data") or {}).get("api") or {}
        hc = ((api_node.get("apiHealthCheck") or {}).get("healthcheckStatus") or {}).get("status")
        print(f"API #{it['num']} | vis={api_node.get('visibility')} | healthcheck={hc} | {it['hub_url']}")


if __name__ == "__main__":
    import sys
    if "--verify-health" in sys.argv:
        verify_healthchecks()
    else:
        res = publish_all_12_apis()
        print(f"[DONE] Published {len(res)}/12 RubricWard APIs on RapidAPI Studio.")

