# utils/sms_utils.py
from sms_ir import SmsIr
from config import Config

def send_otp_sms_template(phone_number: str, otp_code: str) -> bool:
    """
    Sends OTP via sms.ir template (single param: OTP).
    Assumes template 245375 uses a placeholder named 'OTP' like #OTP#.
    """
    try:
        sms_ir = SmsIr(
            Config.SMSIR_API_KEY,
        )

        # Parameter name must match the variable defined in your sms.ir template.
        params = [{"name": "OTP", "value": otp_code}]

        # Replace 'send_verify' with the actual template method exposed by your smsir-python version.
        # Common alternatives: send_pattern, send_fast, send_template, verify, etc.
        sms_ir.send_verify_code(
        phone_number,
        Config.SMSIR_TEMPLATE_ID,
        params,
        )
        return True
    except Exception as e:
        print(f"Failed to send OTP via sms.ir template: {e}")
        return False
