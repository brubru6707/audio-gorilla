import json

# Load the generated state
with open('diverse_amazon_state.json', 'r') as f:
    data = json.load(f)

# Check first 5 products and their reviews
products = list(data['products'].items())[:5]
print("First 5 products and their reviews:\n")
for prod_id, prod_data in products:
    reviews = data['product_reviews'].get(prod_id, [])
    print(f"Product: {prod_data['name'][:70]}")
    print(f"Number of reviews: {len(reviews)}")
    if reviews:
        print(f"First review comment: {reviews[0]['comment'][:100]}")
    print("-" * 80)

# Count total reviews
total_reviews = sum(len(reviews) for reviews in data['product_reviews'].values())
print(f"\nTotal products: {len(data['products'])}")
print(f"Total reviews: {total_reviews}")
print(f"Average reviews per product: {total_reviews / len(data['products']):.2f}")
