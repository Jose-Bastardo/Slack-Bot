import smtplib, ssl
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import datetime
from slack_bolt import App

sender_email=os.environ["sender_email"]

app = App(
    token=os.environ["token"],
    signing_secret=os.environ["signing-secret"]
)

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  print("App Home Working")
  try:
    id=event["user"]
    user = client.users_info(
      user=id
    )
    name=user["user"]["real_name"]
    if name == "Jose Bastardo":
      home_view={
        "type": "home",
        "callback_id": "home_view",
        # body of the view
        "blocks":[
          {
            "type": "actions",
            "elements": [
              {
              "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Send Emails"
                },
                "style": "primary",
                "value": "312321231",
                "action_id": "send_emails_button"
              }
            ]
          }
        ]
      }
    else:
      home_view={
          "type": "home",
          "callback_id": "home_view",

          # body of the view
          "blocks": [
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "*Welcome to your _App's Home_* :tada:"
              }
            },
            {
              "type": "divider"
            },
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
              }
            },
            {
              "type": "actions",
              "elements": [
                {
                  "type": "button",
                  "text": {
                    "type": "plain_text",
                    "text": "Click me!"
                  }
                }
              ]
            }
          ]
        }
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=id,
      # the view object that appears in the app home
      view=home_view
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.command("/email")
def send_email(ack, command, client):
  ack()

  id = command["user_id"]
  user = client.users_info(
    user=id
  )

  name = user["user"]["real_name"]

  if name == "Jose Bastardo" or name == "Adam Conley":
    client.views_open(
      
      trigger_id=command["trigger_id"],
      view={
        "type": "modal",
        "callback_id": "email_modal",
        "title": {
          "type": "plain_text",
          "text": "Email Module"
        },
        "blocks": [
          {
          "type": "input",
          "block_id": "subject",
          "label": {
            "type": "plain_text",
            "text": "Subject"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "subject_id",
              "multiline": False,
              "placeholder": {
                "type": "plain_text",
                "text": "Enter subject of email"
              }
            }
          },
        {
          "type": "input",
          "block_id": "email_input",
          "label": {
            "type": "plain_text",
            "text": "Email"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "text_id",
              "multiline": True,
              "placeholder": {
                "type": "plain_text",
                "text": "Enter message"
              }
            }
          },
          {
            "type": "input",
            "block_id": "channel_select",
            "label": {
              "type": "plain_text",
              "text": "Pick channels from the list"
            },
            "element": {
              "type": "multi_channels_select",
              "action_id": "list_id",
              "placeholder": {
                "type": "plain_text",
                "text": "Select channels"
              }
            },
          }
        ],
        "submit": {
          "type": "plain_text",
          "text": "Submit"
        }
      }
    )

@app.view("email_modal")
def send_emails(ack, client, body, view):
  ack()
  members = []
  emails = []
  
  text=body["view"]["state"]["values"]["email_input"]["text_id"]["value"]
  channels=body["view"]["state"]["values"]["channel_select"]["list_id"]["selected_channels"]
  subject=body["view"]["state"]["values"]["subject"]["subject_id"]["value"]

  for i in channels:
    member_ids = client.conversations_members(
    channel=i
    )
    for x in member_ids["members"]:
      try:
        members.index(x)
      except:
        members.append(x)
  
  for id in members:
    user = client.users_info(
      user=id
    )
    emails.append(user["user"]["profile"]["email"])
  
  text = text.replace('\n', "</br>")
  text = text.replace('\r', "</br>")

  sender_email = os.getenv('sender_email')
  password = os.getenv('password')
  
  port = 465  # For SSL

  for i in emails:
    if i == "josebastardo123@gmail.com":
      message = MIMEMultipart("alternative")
      message["Subject"] = subject
      message["From"] = sender_email
      message["To"] = i

      html = """\
      <html>
        <body>
          <p>
          """ + text + """
          </p>
        </body>
      </html>
      """

      htmlmessage = MIMEText(html, "html")

      message.attach(htmlmessage)

      # Create a secure SSL context
      context = ssl.create_default_context()

      with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, i, message.as_string())

@app.message("!email")
def say_hello(message, say):
  user = message['user']
  print(message["text"])
  #say(f"Hi there, <@{user}>!")

if __name__ == "__main__":
  app.start(port=int(os.environ.get("PORT", 3000)))