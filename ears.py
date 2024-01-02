import time
from db.db_operations import connect_to_mongodb, fetch_data_from_mongodb, save_data_to_mongodb

def respond_to_input(user_input):
    if "hello" in user_input.lower():
        return "Hello! How can I assist you today?"
    elif "how are you" in user_input.lower():
        return "I'm just a computer program, but I'm doing well. Thank you for asking!"
    elif "bye" in user_input.lower():
        return "Goodbye! Have a great day."
    else:
        return "I'm not sure how to respond to that. Can you please ask me something else?"

def save_data_in_bulk(data_list, collection_name):
    collection = connect_to_mongodb(collection_name)
    collection.insert_many(data_list)

def split_and_save_words(user_input, response, collection, eventId):
    words = set(user_input.lower().split()) | set(response.lower().split())

    # Remove repeated words from the collection
    words = list(filter(lambda word: word not in collection, words))

    # Save the words in the collection
    data_to_save = [{"word": word, "createdAt": eventId} for word in words]
    save_data_in_bulk(data_to_save, "words")


def query_and_aggregate_by_words(words):
    words_collection = connect_to_mongodb("words")

    # Query for documents where the "word" field matches any of the provided words
    query_result = words_collection.find({"word": {"$in": words}})

    # Aggregate by eventId
    aggregation_result = words_collection.aggregate([
        {"$match": {"word": {"$in": list(words)}, "createdAt": {"$ne": None}}},  # Convert set to list
        {"$group": {"_id": "$createdAt", "wordCount": {"$sum": 1}, "words": {"$push": "$word"}}},
        {"$sort": {"wordCount": -1}},
        {"$limit": 1}
    ])

    return list(query_result), list(aggregation_result)

def query_event_by_event_id(event_id):
    events_collection = connect_to_mongodb("events")
    result = events_collection.find_one({"createdAt": event_id})
    return result

def main():
    print("Welcome! Type 'bye' to exit.")

    # Reference to the event collection
    event_collection_name = "events"

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'bye':
            print("Goodbye!")
            break

        response = respond_to_input(user_input)
        print("Divakar:", response)

        # Example of saving data to MongoDB
        current_time_epoch = int(time.time())
        collection_name = "words"
        data_to_save = {"user_input": user_input, "response": response, "createdAt": current_time_epoch}
        save_data_to_mongodb(data_to_save, event_collection_name)

        # Fetch data from MongoDB
        fetched_data = fetch_data_from_mongodb(event_collection_name)
        # print("Event captured in training dataset:", fetched_data)

        # Save words to the collection
        split_and_save_words(user_input, response, collection_name, current_time_epoch)

        # Query and aggregate by eventId
        # result = query_and_aggregate_by_event_id(current_time_epoch)
        words = set(user_input.lower().split()) | set(response.lower().split())
        # Remove repeated words from the collection
        words = list(filter(lambda word: word not in collection_name, words))
        query_result, aggregation_result = query_and_aggregate_by_words(words)
        # print("Aggregated Data by EventId:", result)

        if aggregation_result:
            # max_word_count_event_id = aggregation_result[0]["createdAt"]
            print(aggregation_result[0])
            # print("Max Word Count EventId:", max_word_count_event_id)

            # Query event from events collection based on max_word_count_event_id
            event_result = query_event_by_event_id(aggregation_result[0]['_id'])
            print("Matching Event:", event_result)

if __name__ == "__main__":
    main()
