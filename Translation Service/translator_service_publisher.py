import pika
import sys
import tty
import termios

def send_message(text_to_translate):
    # Establish a connection with RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queue (this will only create it if it doesn't already exist)
    channel.queue_declare(queue='translate')

    # Send a message to the 'translate' queue
    channel.basic_publish(exchange='', routing_key='translate', body=text_to_translate)

    

    # Close the connection
    connection.close()

def get_ch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


if __name__== "__main__":
    print("\n You can start entering text to be translated. To escape, press ESC. To end a line, use proper ponctuation ( . , ? , ! ) \n")
    buffer = ""
    while True:
        ch = get_ch()
        print(ch, end='', flush=True)
        buffer += ch
        if ord(ch) == 27:  # ASCII value for ESC
            print("\nESC pressed. Exiting...")
            break
        elif ord(ch) == 127:  # ASCII value for backspace
            buffer = buffer[:-2]
            print('\b \b', end='', flush=True)  # move cursor back, overwrite with space, move cursor back again
        elif buffer[-1] in {'.', '!', '?'}:
            send_message(buffer)
            print("\n [x] Sent %r" % buffer)
            buffer = ""
