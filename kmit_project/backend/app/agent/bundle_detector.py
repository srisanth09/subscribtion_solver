from typing import List, Dict, Any, Tuple

# Known bundling ecosystem definitions
KNOWN_BUNDLES = [
    {
        "provider": "YouTube Premium",
        "category": "video_streaming",
        "covers_services": ["music_streaming"],
        "covers_keywords": ["spotify", "tunewave", "musicbox", "apple music", "youtube music"],
        "description": "YouTube Premium includes full YouTube Music ad-free streaming at no additional charge."
    },
    {
        "provider": "Amazon Prime",
        "category": "e-commerce",
        "covers_services": ["video_streaming", "music_streaming"],
        "covers_keywords": ["prime video", "amazon music"],
        "description": "Amazon Prime membership bundles Prime Video and Prime Music."
    },
    {
        "provider": "Apple One",
        "category": "bundle",
        "covers_services": ["music_streaming", "video_streaming", "cloud_storage"],
        "covers_keywords": ["apple music", "apple tv", "icloud"],
        "description": "Apple One combines Apple Music, Apple TV+, and iCloud into one discounted subscription."
    }
]

class BundleDetector:
    """
    Detects if any active subscription is redundant because another active bundle already covers it.
    """
    
    def check_bundles_and_duplicates(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cross-analyzes all subscriptions to find:
        1. Services redundant due to active bundles.
        2. Duplicate / overlapping services in the exact same functional category (e.g., TuneWave vs MusicBox).
        """
        merchant_names_lower = {s["merchant"].lower(): s for s in subscriptions}
        
        # 1. Bundle detection
        for bundle in KNOWN_BUNDLES:
            bundle_provider_lower = bundle["provider"].lower()
            if bundle_provider_lower in merchant_names_lower:
                # User has this bundle! Check if they are paying for covered services separately
                for s in subscriptions:
                    if s["merchant"].lower() != bundle_provider_lower:
                        # Check category or keywords
                        if s.get("category") in bundle["covers_services"] or any(kw in s["merchant"].lower() for kw in bundle["covers_keywords"]):
                            s["is_bundled"] = True
                            s["bundle_provider"] = bundle["provider"]
                            s["bundle_description"] = bundle["description"]

        # 2. Duplicate / Overlapping service detection (e.g. 2 music streaming apps)
        category_map: Dict[str, List[Dict[str, Any]]] = {}
        for s in subscriptions:
            cat = s.get("category")
            if cat:
                if cat not in category_map:
                    category_map[cat] = []
                category_map[cat].append(s)

        for cat, subs in category_map.items():
            if len(subs) > 1:
                # Multiple subscriptions in the same category!
                # Sort by usage (most recently used first)
                sorted_subs = sorted(subs, key=lambda x: x.get("last_used_days_ago", 999))
                most_active = sorted_subs[0]
                
                for s in sorted_subs:
                    s["is_duplicate_detected"] = True
                    s["duplicate_category"] = cat
                    # If this is not the most active, set counterpart as the most active
                    if s["merchant"] != most_active["merchant"]:
                        s["duplicate_counterpart"] = f"{most_active['merchant']} (used {most_active.get('last_used_days_ago')} days ago)"
                    else:
                        s["duplicate_counterpart"] = f"{sorted_subs[1]['merchant']} (used {sorted_subs[1].get('last_used_days_ago')} days ago)"

        return subscriptions

bundle_detector = BundleDetector()
