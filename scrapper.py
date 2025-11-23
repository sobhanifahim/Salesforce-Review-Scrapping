import requests
import pandas as pd

listing_id = "a0N300000024XvyEAE"
page_length = 50     # page can be bigger (case specific)
page_number = 1
all_reviews = []

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.6",
    "origin": "https://appexchange.salesforce.com",
    "referer": "https://appexchange.salesforce.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

while True:
    url = (
        "https://api.appexchange.salesforce.com/services/apexrest/reviews"
        f"?listingId={listing_id}&pageLength={page_length}&pageNumber={page_number}&sort=mr"
    )

    print(f"\nFetching page {page_number}...")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("HTTP error:", r.status_code)
        break

    data = r.json()

    if page_number == 1:
        print("totalReviewCount reported by API:", data.get("totalReviewCount"))

    reviews = data.get("reviews", [])
    print("reviews returned this page:", len(reviews))

    if not reviews:
        print("No more reviews returned. Stopping.")
        break

    for rev in reviews:
        name = rev.get("user", {}).get("name")
        rating = rev.get("rating")
        review_date = rev.get("reviewDate")

        title = None
        comment = None
        for q in rev.get("questionResponses", []):
            if q.get("questionName") == "Title":
                title = q.get("response")
            elif q.get("questionName") == "Comments":
                comment = q.get("response")

        all_reviews.append({
            "customer_name": name,
            "review_title": title,
            "review_comment": comment,
            "rating": rating,
            "review_date": review_date
        })

    # some versions include hasMore; rely on both hasMore + empty-page stop
    has_more = data.get("hasMore")
    if has_more is False:
        print("API says hasMore=false. Stopping.")
        break

    page_number += 1

df = pd.DataFrame(all_reviews)
df.to_excel("appex_reviews_public.xlsx", index=False)
print("\nSaved:", "appex_reviews_public.xlsx")
print("Total scraped:", len(df))
