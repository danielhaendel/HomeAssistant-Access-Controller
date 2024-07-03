import paho.mqtt.client as mqtt
import pymysql
import threading
import time

# MariaDB connection details
db_host = 'your_mariadb_host'
db_user = 'your_mariadb_user'
db_password = 'your_mariadb_password'
db_name = 'access_control'

# MQTT settings
mqtt_broker = "192.168.1.10"
mqtt_port = 1883

clients = {
    "arduinoClient1": "Client 1",
    "arduinoClient2": "Client 2"
}

# Watchdog settings
watchdog_interval = 30  # Interval in seconds

def connect_db():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

def check_user_access(client_id, user_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE client_id=%s AND user_id=%s"
            cursor.execute(sql, (client_id, user_id))
            result = cursor.fetchone()
            if result and result['access_granted']:
                return True
            return False
    finally:
        connection.close()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("home/assistant/entry")

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} {msg.payload}")
    payload = msg.payload.decode()
    client_id, user_id = payload.split(',')
    if client_id in clients:
        print(f"Access attempt by {clients[client_id]} with user ID: {user_id}")
        if check_user_access(client_id, user_id):
            print(f"Access granted for user ID: {user_id}")
            # Hier kannst du auch eine MQTT-Nachricht senden, um Zugang zu gewähren
        else:
            print(f"Access denied for user ID: {user_id}")
            # Hier kannst du auch eine MQTT-Nachricht senden, um Zugang zu verweigern

def watchdog(client):
    while True:
        if not client.is_connected():
            print("MQTT client is not connected. Attempting to reconnect...")
            client.reconnect()
        # Hier können weitere Überprüfungen hinzugefügt werden
        time.sleep(watchdog_interval)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)

    # Start Watchdog thread
    watchdog_thread = threading.Thread(target=watchdog, args=(client,))
    watchdog_thread.daemon = True
    watchdog_thread.start()

    client.loop_forever()

if __name__ == "__main__":
    main()
