"""
Wrapper para a Meta Marketing API v21.
Documentação: https://developers.facebook.com/docs/marketing-api
"""
import requests
from typing import Optional, Union

API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


class MetaAdsAPI:
    def __init__(self, access_token: str, ad_account_id: str):
        self.access_token = access_token
        # Garante formato act_XXXX
        if not ad_account_id.startswith("act_"):
            ad_account_id = f"act_{ad_account_id}"
        self.ad_account_id = ad_account_id
        self.session = requests.Session()
        self.session.params = {"access_token": access_token}  # type: ignore

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{BASE_URL}/{path}"
        resp = self.session.get(url, params=params or {})
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise ValueError(f"Meta API error: {data['error']['message']}")
        return data

    def _post(self, path: str, data: dict = None) -> dict:
        url = f"{BASE_URL}/{path}"
        resp = self.session.post(url, data=data or {})
        resp.raise_for_status()
        result = resp.json()
        if "error" in result:
            raise ValueError(f"Meta API error: {result['error']['message']}")
        return result

    # ─── CAMPANHAS ────────────────────────────────────────────────────────────

    def get_campaigns(
        self,
        status_filter: str = "ACTIVE",
        limit: int = 25,
    ) -> list[dict]:
        """Lista campanhas da conta com métricas básicas."""
        fields = "id,name,status,objective,budget_remaining,daily_budget,lifetime_budget,start_time,stop_time,created_time"
        params = {
            "fields": fields,
            "limit": limit,
        }
        if status_filter and status_filter != "ALL":
            params["effective_status"] = f'["{status_filter}"]'
        data = self._get(f"{self.ad_account_id}/campaigns", params)
        return data.get("data", [])

    def create_campaign(
        self,
        name: str,
        objective: str,
        status: str = "PAUSED",
        daily_budget: Optional[int] = None,
        lifetime_budget: Optional[int] = None,
        start_time: Optional[str] = None,
        stop_time: Optional[str] = None,
        special_ad_categories: list = None,
    ) -> dict:
        """
        Cria uma campanha.
        objective: OUTCOME_AWARENESS | OUTCOME_TRAFFIC | OUTCOME_ENGAGEMENT |
                   OUTCOME_LEADS | OUTCOME_APP_PROMOTION | OUTCOME_SALES
        budgets em centavos (ex: R$50/dia = 5000)
        """
        payload = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": json_encode(special_ad_categories or ["NONE"]),
        }
        if daily_budget:
            payload["daily_budget"] = str(daily_budget)
        if lifetime_budget:
            payload["lifetime_budget"] = str(lifetime_budget)
        if start_time:
            payload["start_time"] = start_time
        if stop_time:
            payload["stop_time"] = stop_time
        return self._post(f"{self.ad_account_id}/campaigns", payload)

    def update_campaign_status(self, campaign_id: str, status: str) -> dict:
        """Altera status: ACTIVE | PAUSED | DELETED | ARCHIVED"""
        return self._post(campaign_id, {"status": status})

    # ─── ADSETS ───────────────────────────────────────────────────────────────

    def get_adsets(
        self,
        campaign_id: Optional[str] = None,
        status_filter: str = "ACTIVE",
        limit: int = 25,
    ) -> list[dict]:
        """Lista adsets. Filtra por campanha se campaign_id fornecido."""
        fields = "id,name,status,daily_budget,lifetime_budget,targeting,optimization_goal,billing_event,bid_amount,start_time,end_time,campaign_id"
        params = {"fields": fields, "limit": limit}
        if status_filter and status_filter != "ALL":
            params["effective_status"] = f'["{status_filter}"]'
        if campaign_id:
            data = self._get(f"{campaign_id}/adsets", params)
        else:
            data = self._get(f"{self.ad_account_id}/adsets", params)
        return data.get("data", [])

    def create_adset(
        self,
        campaign_id: str,
        name: str,
        optimization_goal: str,
        billing_event: str,
        daily_budget: Optional[int] = None,
        lifetime_budget: Optional[int] = None,
        targeting: Optional[dict] = None,
        bid_amount: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        status: str = "PAUSED",
    ) -> dict:
        """
        Cria um adset.
        optimization_goal: LINK_CLICKS | IMPRESSIONS | REACH | LEAD_GENERATION |
                           OFFSITE_CONVERSIONS | LANDING_PAGE_VIEWS | etc.
        billing_event: IMPRESSIONS | LINK_CLICKS | etc.
        targeting: dict com geo_locations, age_min, age_max, interests etc.
        """
        import json
        payload = {
            "campaign_id": campaign_id,
            "name": name,
            "optimization_goal": optimization_goal,
            "billing_event": billing_event,
            "status": status,
            "targeting": json.dumps(targeting or {
                "geo_locations": {"countries": ["BR"]},
                "age_min": 18,
                "age_max": 65,
            }),
        }
        if daily_budget:
            payload["daily_budget"] = str(daily_budget)
        elif lifetime_budget:
            payload["lifetime_budget"] = str(lifetime_budget)
        else:
            # Meta API requer orçamento no adset quando a campanha não usa CBO
            payload["daily_budget"] = "5000"  # R$50/dia como fallback seguro
        if bid_amount:
            payload["bid_amount"] = str(bid_amount)
        if start_time:
            payload["start_time"] = start_time
        if end_time:
            payload["end_time"] = end_time
        return self._post(f"{self.ad_account_id}/adsets", payload)

    def update_adset_status(self, adset_id: str, status: str) -> dict:
        return self._post(adset_id, {"status": status})

    # ─── ADS ──────────────────────────────────────────────────────────────────

    def get_ads(
        self,
        adset_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        status_filter: str = "ACTIVE",
        limit: int = 25,
    ) -> list[dict]:
        """Lista anúncios. Filtra por adset ou campanha se fornecido."""
        fields = "id,name,status,adset_id,campaign_id,creative,created_time,updated_time"
        params = {"fields": fields, "limit": limit}
        if status_filter and status_filter != "ALL":
            params["effective_status"] = f'["{status_filter}"]'
        if adset_id:
            data = self._get(f"{adset_id}/ads", params)
        elif campaign_id:
            data = self._get(f"{campaign_id}/ads", params)
        else:
            data = self._get(f"{self.ad_account_id}/ads", params)
        return data.get("data", [])

    def create_ad(
        self,
        adset_id: str,
        name: str,
        creative_id: Optional[str] = None,
        creative_spec: Optional[dict] = None,
        status: str = "PAUSED",
    ) -> dict:
        """
        Cria um anúncio. Fornece creative_id (existente) ou creative_spec (novo).
        creative_spec exemplo: {
            "object_story_spec": {
                "page_id": "PAGE_ID",
                "link_data": {
                    "link": "https://...",
                    "message": "Texto do anúncio",
                    "name": "Título",
                    "description": "Descrição",
                    "image_hash": "HASH_DA_IMAGEM"
                }
            }
        }
        """
        import json
        payload = {
            "adset_id": adset_id,
            "name": name,
            "status": status,
        }
        if creative_id:
            payload["creative"] = json.dumps({"creative_id": creative_id})
        elif creative_spec:
            # Garante que o criativo tenha um nome (obrigatório pela API)
            creative_payload = dict(creative_spec)
            if "name" not in creative_payload:
                creative_payload["name"] = name
            # Primeiro cria o creative, depois o ad
            creative = self._post(
                f"{self.ad_account_id}/adcreatives",
                {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                 for k, v in creative_payload.items()}
            )
            payload["creative"] = json.dumps({"creative_id": creative["id"]})
        return self._post(f"{self.ad_account_id}/ads", payload)

    def update_ad_status(self, ad_id: str, status: str) -> dict:
        return self._post(ad_id, {"status": status})

    # ─── INSIGHTS / MÉTRICAS ──────────────────────────────────────────────────

    def get_insights(
        self,
        object_id: Optional[str] = None,
        level: str = "campaign",
        date_preset: str = "last_30d",
        date_start: Optional[str] = None,
        date_stop: Optional[str] = None,
        breakdowns: Optional[list[str]] = None,
        time_increment: Optional[int] = None,
        limit: int = 25,
    ) -> list[dict]:
        """
        Busca métricas de performance.
        level: account | campaign | adset | ad
        date_preset: today | yesterday | last_7d | last_14d | last_30d |
                     last_month | this_month | last_quarter | this_year
        breakdowns: age, gender, country, publisher_platform, device_platform
        """
        fields = (
            "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,"
            "impressions,reach,clicks,ctr,cpm,cpp,cpc,"
            "spend,frequency,"
            "actions,cost_per_action_type,"
            "video_avg_time_watched_actions,video_p25_watched_actions,"
            "video_p50_watched_actions,video_p75_watched_actions,video_p95_watched_actions"
        )
        params = {
            "fields": fields,
            "level": level,
            "limit": limit,
        }
        if date_start and date_stop:
            params["time_range"] = f'{{"since":"{date_start}","until":"{date_stop}"}}'
        else:
            params["date_preset"] = date_preset
        if breakdowns:
            params["breakdowns"] = ",".join(breakdowns)
        if time_increment is not None:
            params["time_increment"] = str(time_increment)

        target = object_id or self.ad_account_id
        data = self._get(f"{target}/insights", params)
        return data.get("data", [])

    def get_account_overview(self) -> dict:
        """Resumo geral da conta de anúncios."""
        fields = "id,name,account_status,currency,timezone_name,amount_spent,balance,spend_cap,funding_source_details"
        return self._get(self.ad_account_id, {"fields": fields})

    # ─── TESTES A/B ───────────────────────────────────────────────────────────

    def create_ab_test(
        self,
        name: str,
        campaign_ids: list[str],
        objective: str,
        end_time: str,
    ) -> dict:
        """
        Cria um teste A/B entre campanhas.
        Requer pelo menos 2 campaign_ids.
        end_time no formato ISO: "2025-04-30T00:00:00-0300"
        """
        import json
        payload = {
            "name": name,
            "cells": json.dumps([{"campaign_ids": [c]} for c in campaign_ids]),
            "objective": objective,
            "end_time": end_time,
            "type": "SPLIT_TEST",
        }
        return self._post(f"{self.ad_account_id}/abtests", payload)

    def get_ab_tests(self) -> list[dict]:
        """Lista testes A/B da conta."""
        fields = "id,name,status,type,objective,start_time,end_time,cells"
        data = self._get(
            f"{self.ad_account_id}/abtests",
            {"fields": fields}
        )
        return data.get("data", [])

    # ─── CRIATIVOS ────────────────────────────────────────────────────────────

    def get_ad_creatives(self, ad_id: str) -> dict:
        """Detalhes do criativo de um anúncio específico."""
        fields = "id,name,title,body,image_url,video_id,object_story_spec,thumbnail_url,status"
        data = self._get(f"{ad_id}/adcreatives", {"fields": fields})
        return data.get("data", [])

    def upload_image(self, image_path: str) -> dict:
        """Faz upload de uma imagem e retorna o hash para usar em criativos."""
        import os
        url = f"{BASE_URL}/{self.ad_account_id}/adimages"
        with open(image_path, "rb") as f:
            filename = os.path.basename(image_path)
            resp = requests.post(
                url,
                data={"access_token": self.access_token},
                files={"filename": (filename, f)},
            )
        resp.raise_for_status()
        result = resp.json()
        if "error" in result:
            raise ValueError(f"Meta API error: {result['error']['message']}")
        images = result.get("images", {})
        if images:
            first_key = list(images.keys())[0]
            return images[first_key]
        return result

    # ─── PÁGINAS ──────────────────────────────────────────────────────────────

    def get_pages(self) -> list[dict]:
        """Lista as páginas do Facebook disponíveis na conta."""
        data = self._get("me/accounts", {"fields": "id,name,access_token,category"})
        return data.get("data", [])

    def get_lead_gen_forms(self, page_id: str) -> list[dict]:
        """Lista formulários de Lead Ads de uma página."""
        data = self._get(f"{page_id}/leadgen_forms", {"fields": "id,name,status"})
        return data.get("data", [])


def json_encode(value) -> str:
    import json
    return json.dumps(value)
