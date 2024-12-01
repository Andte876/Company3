#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/syslog.h>
#include <syslog.h>
#include <time.h>
#include <unistd.h>
#include <mdb/connection.h>
#include <mdb/error.h>
#include <mdb/subscriber.h>

// Code ------------------------------------------------------------

// Add JSON library for parsing JSON data
#include <jansson.h> 

// Add libcurl for HTTP requests (lightweight HTTP client library)
#include <curl/curl.h>

// ------------------------------------------------------------------
typedef struct channel_identifier {
    char* topic;
    char* source;
} channel_identifier_t;

static void on_connection_error(mdb_error_t* error, void* user_data) {
    (void)user_data;

    syslog(LOG_ERR, "Got connection error: %s, Aborting...", error->message);
    abort();
}

// Code ----------------------------------------------------------------

// Function to handle the response from the HTTP request
static size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    (void)contents; // Suppress unused parameter warning
    (void)userp;    // Suppress unused parameter warning
    
    // This callback is needed by curl, but we don't need to do anything with the response
    return size * nmemb;
}

// Function to send HTTP POST request to the specified URL with the JSON data
static void send_http_request(const char* url, const char* data) {
    
    // Initialize curl
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if(curl) {

        // Set the URL and data for the HTTP POST request
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);

        // Perform the HTTP POST request
        res = curl_easy_perform(curl);
        if(res != CURLE_OK)
            syslog(LOG_ERR, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        // Clean up
        curl_easy_cleanup(curl);
    }
}

// Function to handle incoming object detection data from the Metadata Broker
static void on_message(const mdb_message_t* message, void* user_data) {
    
    // Get the timestamp and payload from the message. Payload is the JSON data.
    const struct timespec* timestamp     = mdb_message_get_timestamp(message);
    const mdb_message_payload_t* payload = mdb_message_get_payload(message);
    
    // Get the channel identifier from the user data
    channel_identifier_t* channel_identifier = (channel_identifier_t*)user_data;
    
    // Parse JSON payload into a JSON object: root, using Jansson library
    json_error_t error;
    json_t* root = json_loadb((const char*)payload->data, payload->size, 0, &error);
    
    // Check if the JSON object was created successfully
    if (!root) {
        syslog(LOG_ERR, "JSON parsing error: %s", error.text);
        return;
    }

    // Extract frame object
    json_t* frame = json_object_get(root, "frame");
    if (!json_is_object(frame)) {
        syslog(LOG_ERR, "Invalid frame object");
        json_decref(root);
        return;
    }

    // Extract observations array
    json_t* observations = json_object_get(frame, "observations");
    if (!json_is_array(observations)) {
        syslog(LOG_ERR, "Invalid observations array");
        json_decref(root);
        return;
    }

    // Iterate through observations in the observations array
    size_t index;
    json_t* observation;
    json_array_foreach(observations, index, observation) {
        
        // Extract track_id and class from the observation
        json_t* track_id = json_object_get(observation, "track_id");
        json_t* class_obj = json_object_get(observation, "class");
        
        // Check if the class object is valid
        if (json_is_object(class_obj)) {
            
            // Extract type and score from the class object 
            json_t* type = json_object_get(class_obj, "type");
            json_t* score = json_object_get(class_obj, "score");
            
            // Check if type and score are valid
            if (json_is_string(type) && json_is_number(score)) {
                
                // Get the string value of type and the number value of score
                const char* type_value = json_string_value(type);
                double score_value = json_number_value(score);
                
                // Log the detected object information
                syslog(LOG_INFO,
                       "Detected object - Topic: %s, Source: %s, Time: %lld.%.9ld, Track ID: %s, Type: %s, Score: %.4f",
                       channel_identifier->topic,
                       channel_identifier->source,
                       (long long)timestamp->tv_sec,
                       timestamp->tv_nsec,
                       json_string_value(track_id),
                       type_value,
                       score_value);
                
                // Prepare data for HTTP request 
                char data[256];
                snprintf(data, sizeof(data), 
                         "topic=%s&source=%s&time=%lld.%.9ld&type=%s&score=%.4f",
                         channel_identifier->topic,
                         channel_identifier->source,
                         (long long)timestamp->tv_sec,
                         timestamp->tv_nsec,
                         type_value,
                         score_value);

                // Send HTTP request
                send_http_request("http://192.168.1.123:5000/camera/data", data); // TODO: Change to the correct IP address

                // Add error handling for the HTTP request
                // ...
            }
        }
    }
    
    // Clean up
    json_decref(root);
}

// ------------------------------------------------------------------


static void on_done_subscriber_create(const mdb_error_t* error, void* user_data) {
    if (error != NULL) {
        syslog(LOG_ERR, "Got subscription error: %s, Aborting...", error->message);
        abort();
    }
    channel_identifier_t* channel_identifier = (channel_identifier_t*)user_data;

    syslog(LOG_INFO,
           "Subscribed to %s (%s)...",
           channel_identifier->topic,
           channel_identifier->source);
}

static void sig_handler(int signum) {
    (void)signum;
    // Do nothing, just let pause in main return.
}

int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    syslog(LOG_INFO, "Subscriber started...");

    // source corresponds to the video channel number, should be 1
    channel_identifier_t channel_identifier    = {.topic =
                                                      "com.axis.analytics_scene_description.v0.beta",
                                                  .source = "1"};
    mdb_error_t* error                         = NULL;
    mdb_subscriber_config_t* subscriber_config = NULL;
    mdb_subscriber_t* subscriber               = NULL;
    syslog(LOG_INFO,"%s", channel_identifier.topic);

    mdb_connection_t* connection = mdb_connection_create(on_connection_error, NULL, &error);
    if (error != NULL) {
        goto end;
    }

    subscriber_config = mdb_subscriber_config_create(channel_identifier.topic,
                                                     channel_identifier.source,
                                                     on_message,
                                                     &channel_identifier,
                                                     &error);
    if (error != NULL) {
        goto end;
    }

    subscriber = mdb_subscriber_create_async(connection,
                                             subscriber_config,
                                             on_done_subscriber_create,
                                             &channel_identifier,
                                             &error);
    if (error != NULL) {
        goto end;
    }

    // Add signal handler to allow for cleanup on ordered termination.
    (void)signal(SIGTERM, sig_handler);

    pause();

end:
    if (error != NULL) {
        syslog(LOG_ERR, "%s", error->message);
    }

    mdb_error_destroy(&error);
    mdb_subscriber_config_destroy(&subscriber_config);
    mdb_subscriber_destroy(&subscriber);
    mdb_connection_destroy(&connection);

    syslog(LOG_INFO, "Subscriber closed...");

    return 0;
}
