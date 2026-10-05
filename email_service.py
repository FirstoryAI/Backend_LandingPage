import resend


def send_welcome_email(recipient: str):
    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": "Firstory에 가입하신 여러분을 환영합니다!",
        "html": """
            <h1>등록이 완료되었습니다!</h1>
            <p>이메일 등록이 정상적으로 완료되었습니다.</p>
            <p>출시 3일 전에 다시 알려드리겠습니다.</p>
        """
    })

    return response