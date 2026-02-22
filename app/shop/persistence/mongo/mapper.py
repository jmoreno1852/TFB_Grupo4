from typing import Any, Dict

from app.shop.domain.entities import ShopListing

#No need to map ShopItemView as it is a view model for the front end
def doc_to_listing(doc: Dict[str, Any]) -> ShopListing:
    """
    Mongo doc to ShopListing domain entity.
    """
    return ShopListing(
        item_id=doc["item_id"],
        available_from=doc["available_from"],
        available_to=doc["available_to"],
    )


def listing_to_doc(listing: ShopListing) -> Dict[str, Any]:
    """
    ShopListing domain entity to Mongo document.
    """
    return {
        "item_id": listing.item_id,
        "available_from": listing.available_from,
        "available_to": listing.available_to,
    }