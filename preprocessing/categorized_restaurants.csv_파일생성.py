import pandas as pd
import openai

# 1. Load the CSV file and extract unique categories
file_path = 'full_combined_with_address_map.csv'
df = pd.read_csv(file_path, index_col=0)

# Get the unique 'category' values
unique_categories = df['category'].unique()

# Save the unique categories to a .txt file
with open('unique_categories.txt', 'w') as f:
    for category in unique_categories:
        f.write(f"{category}\n")

print("Unique categories have been saved to 'unique_categories.txt'")

# 2. Initialize OpenAI client with the API key
api_key = 'your_openai_api_key_here'  # Replace with your actual API key
client = openai.Client(api_key=api_key)

# Read unique categories from the .txt file
with open('unique_categories.txt', 'r') as f:
    categories = [line.strip() for line in f.readlines()]

# Function to categorize each category using GPT-4 mini
def categorize_with_gpt(category):
    messages = [
        {"role": "system", "content": "You are an assistant that categorizes restaurant types. Just provide the category in a 'restaurant type: category' format. No explanation."},
        {"role": "user", "content": f"Classify the following restaurant types into one of three groups: 1. 식사 2. 카페/디저트 3. 기타. restaurant types: {category}"}
    ]
    
    try:
        # OpenAI API call using the correct client.chat.completions.create structure
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract the response in concise format
        result = response.choices[0].message.content.strip()
        return f"{category}: {result.split(':')[-1].strip()}"
    
    except Exception as e:
        print(f"Error with categorizing {category}: {str(e)}")
        return f"{category}: 기타"  # Default to '기타' if something goes wrong

# Classify each category and save results
with open('simple_categorized_unique_categories.txt', 'w') as f:
    for category in categories:
        classification = categorize_with_gpt(category)
        f.write(f"{classification}\n")
        print(classification)

print("Category classifications have been saved to 'simple_categorized_unique_categories.txt'")

# 3. Categorize and save results into separate lists
meal_categories = []
cafe_dessert_categories = []
other_categories = []

# Read the file with the categorized restaurant types
with open('simple_categorized_unique_categories.txt', 'r') as f:
    for line in f:
        # Split the line into restaurant_type and category
        restaurant_type, category = line.strip().split(': ')
        
        # Append to the respective list based on the category
        if category == '식사':
            meal_categories.append(restaurant_type)
        elif category == '카페/디저트':
            cafe_dessert_categories.append(restaurant_type)
        else:
            other_categories.append(restaurant_type)

# Print the results
print(f"식사: {meal_categories}")
print(f"카페/디저트: {cafe_dessert_categories}")
print(f"기타: {other_categories}")

# Optionally, save the results to a file
with open('categorized_restaurants.txt', 'w') as f:
    f.write(f"식사: {meal_categories}\n")
    f.write(f"카페/디저트: {cafe_dessert_categories}\n")
    f.write(f"기타: {other_categories}\n")

print("Results have been saved to 'categorized_restaurants.txt'")

# 4. Process categorized restaurants to a DataFrame and save it to a CSV file
# Read the contents of the 'categorized_restaurants.txt' file
with open('categorized_restaurants.txt', 'r') as f:
    lines = f.readlines()

# Initialize empty lists for each category
meal_categories = []
cafe_dessert_categories = []
other_categories = []

# Process each line and populate the lists
for line in lines:
    if line.startswith("식사:"):
        meal_categories = line.strip()[5:-1].split(', ')  # Remove '식사:' and brackets
    elif line.startswith("카페/디저트:"):
        cafe_dessert_categories = line.strip()[9:-1].split(', ')  # Remove '카페/디저트:' and brackets
    elif line.startswith("기타:"):
        other_categories = line.strip()[5:-1].split(', ')  # Remove '기타:' and brackets

# Create a list of dictionaries for easier DataFrame creation
data = [
    {"purpose": "식사", "category": ', '.join(meal_categories)},
    {"purpose": "카페/디저트", "category": ', '.join(cafe_dessert_categories)},
    {"purpose": "기타", "category": ', '.join(other_categories)}
]

# Create the DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('categorized_restaurants.csv', index=False)

# Display the DataFrame
print(df)
