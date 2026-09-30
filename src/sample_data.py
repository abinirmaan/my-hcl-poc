SAMPLE_REQUIREMENT = """REQ-LOGIN-01
A customer can sign in using a registered email address and password.
After five consecutive failed sign-in attempts, the account must be locked for 30 minutes.
The failed-attempt counter must reset after a successful sign-in.
The lockout message must not reveal whether the email address is registered.
An audit event must record the lock and unlock actions."""

