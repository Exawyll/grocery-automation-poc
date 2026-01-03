import requests
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class CarrefourAPIService:
    """Service pour l'intégration avec l'API Carrefour"""

    def __init__(self):
        self.api_key = os.getenv("CARREFOUR_API_KEY", "")
        self.api_url = os.getenv("CARREFOUR_API_URL", "https://api.carrefour.fr/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def search_product(self, product_name: str, limit: int = 5) -> List[Dict]:
        """
        Recherche un produit dans l'API Carrefour

        Args:
            product_name: Nom du produit à rechercher
            limit: Nombre maximum de résultats

        Returns:
            Liste de produits trouvés
        """
        if not self.api_key:
            # Mode simulation si pas de clé API
            return self._mock_search_product(product_name, limit)

        try:
            response = requests.get(
                f"{self.api_url}/products/search",
                headers=self.headers,
                params={
                    "q": product_name,
                    "limit": limit
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("products", [])
        except requests.RequestException as e:
            print(f"Erreur lors de la recherche de produit: {e}")
            return self._mock_search_product(product_name, limit)

    def get_product_price(self, product_id: str) -> Dict:
        """
        Récupère le prix d'un produit

        Args:
            product_id: ID du produit

        Returns:
            Informations sur le prix du produit
        """
        if not self.api_key:
            return self._mock_get_product_price(product_id)

        try:
            response = requests.get(
                f"{self.api_url}/products/{product_id}/price",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération du prix: {e}")
            return self._mock_get_product_price(product_id)

    def get_availability(self, product_id: str, store_id: str) -> Dict:
        """
        Vérifie la disponibilité d'un produit dans un magasin

        Args:
            product_id: ID du produit
            store_id: ID du magasin

        Returns:
            Informations sur la disponibilité
        """
        if not self.api_key:
            return self._mock_get_availability(product_id, store_id)

        try:
            response = requests.get(
                f"{self.api_url}/products/{product_id}/availability",
                headers=self.headers,
                params={"store_id": store_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur lors de la vérification de disponibilité: {e}")
            return self._mock_get_availability(product_id, store_id)

    def estimate_shopping_list_cost(self, items: List[Dict]) -> Dict:
        """
        Estime le coût total d'une liste de courses

        Args:
            items: Liste d'articles avec quantités

        Returns:
            Estimation du coût total
        """
        total_cost = 0.0
        detailed_items = []

        for item in items:
            product_name = item.get("name", "")
            quantity = item.get("quantity", 1)

            # Rechercher le produit
            products = self.search_product(product_name, limit=1)

            if products:
                product = products[0]
                price = product.get("price", 0.0)
                item_cost = price * quantity
                total_cost += item_cost

                detailed_items.append({
                    "name": product_name,
                    "quantity": quantity,
                    "unit_price": price,
                    "total_price": item_cost,
                    "product_id": product.get("id")
                })

        return {
            "total_cost": round(total_cost, 2),
            "currency": "EUR",
            "items": detailed_items,
            "item_count": len(detailed_items)
        }

    # Méthodes de simulation pour le développement
    def _mock_search_product(self, product_name: str, limit: int) -> List[Dict]:
        """Simulation de recherche de produit"""
        mock_products = {
            "tomate": [{"id": "P001", "name": "Tomates en grappe", "price": 3.50, "unit": "kg"}],
            "oignon": [{"id": "P002", "name": "Oignons jaunes", "price": 1.80, "unit": "kg"}],
            "carotte": [{"id": "P003", "name": "Carottes bio", "price": 2.20, "unit": "kg"}],
            "poulet": [{"id": "P004", "name": "Filet de poulet", "price": 8.90, "unit": "kg"}],
            "riz": [{"id": "P005", "name": "Riz basmati", "price": 4.50, "unit": "kg"}],
        }

        product_name_lower = product_name.lower()
        for key in mock_products:
            if key in product_name_lower:
                return mock_products[key][:limit]

        return [{"id": "P999", "name": product_name, "price": 5.00, "unit": "unité"}]

    def _mock_get_product_price(self, product_id: str) -> Dict:
        """Simulation de récupération de prix"""
        return {
            "product_id": product_id,
            "price": 5.00,
            "currency": "EUR",
            "unit": "unité"
        }

    def _mock_get_availability(self, product_id: str, store_id: str) -> Dict:
        """Simulation de vérification de disponibilité"""
        return {
            "product_id": product_id,
            "store_id": store_id,
            "available": True,
            "stock_level": "high"
        }
