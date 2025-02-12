from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Message
from .forms import MessageForm
from django.conf import settings
import openai

openai.api_key = settings.OPENAI_API_KEY

def chat_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    messages = Message.objects.filter(customer=customer)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = form.save(commit=False)
            user_message.customer = customer
            user_message.is_user = True
            user_message.save()

            # ✅ Create Assistant if not exists
            if not customer.assistant_id:
                assistant = openai.beta.assistants.create(
                    name=f"Assistant for {customer.name}",
                    instructions="You are a restaurant assistant. Respond based on menu and availability, and provide recommendations, reservations, and hours of operation. Always be sure about customer sensitive information, like payment details, order, reservation, and personal information. If you are unsure, ask for help. Be polite and helpful.",
                    model="gpt-4"
                )
                customer.assistant_id = assistant.id
                customer.save()

            # ✅ Create Thread if not exists
            if not customer.thread_id:
                thread = openai.beta.threads.create()
                customer.thread_id = thread.id
                customer.save()

            # Send user message
            openai.beta.threads.messages.create(
                thread_id=customer.thread_id,
                role="user",
                content=user_message.content
            )

            # Run Assistant
            run = openai.beta.threads.runs.create(
                thread_id=customer.thread_id,
                assistant_id=customer.assistant_id
            )

            # ✅ Polling the Assistant's Response
            import time
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=customer.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(1)  # Wait before checking again

            # ✅ Get the latest Assistant message
            response = openai.beta.threads.messages.list(thread_id=customer.thread_id)
            assistant_reply = None
            for message in response.data:
                if message.role == 'assistant':
                    assistant_reply = message.content[0].text.value
                    break

            # Save Assistant's reply
            if assistant_reply:
                Message.objects.create(customer=customer, content=assistant_reply, is_user=False)

            return redirect('chat', customer_id=customer.id)
    else:
        form = MessageForm()

    return render(request, 'assistants/chat.html', {'messages': messages, 'form': form, 'customer': customer})
