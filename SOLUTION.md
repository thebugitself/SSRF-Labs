# SSRF Labs - Solutions

This document contains detailed explanations and payloads for each level. **Do not read this file until you have attempted the challenges yourself.**

---

## Level 1 - Easy (No Protection)

### Vulnerability

The backend performs a raw HTTP request to whatever URL the user provides. There is zero validation, sanitization, or filtering. This is the most basic form of SSRF.

### Exploitation

Inside the container, a hidden internal admin service is running on `127.0.0.1:80`. It is not exposed to the host, but the web application can reach it because both services share the same loopback interface.

**Payload to retrieve the flag:**

```
http://127.0.0.1/flag
```

**Payload to retrieve secret data:**

```
http://127.0.0.1/secret-data
```

### Expected Response

```json
{
  "flag": "FLAG{ssrf_m4st3r_0f_th3_1nt3rn4l_n3tw0rk}",
  "message": "You have successfully exploited SSRF to reach the internal service."
}
```

### Why This Works

The server-side code simply takes the URL from the form input and passes it directly to an HTTP client (`httpx`). Because the internal admin service is bound to `127.0.0.1:80` inside the same container, the request succeeds server-side -- even though the service is completely invisible from outside the container.

---

## Level 2 - Medium (Blacklist Bypass)

### Vulnerability

The backend implements a naive keyword blacklist that checks the raw URL string for the following terms:
- `127.0.0.1`
- `localhost`
- `0.0.0.0`
- `::1`
- `[::1]`

The flaw is that IP addresses have many alternative representations that are semantically equivalent but textually different.

### Exploitation

Since the common loopback representations are blocked, you need to use alternative IP encodings that still resolve to `127.0.0.1`.

**Method 1: Decimal IP notation**

The IP `127.0.0.1` can be expressed as a single 32-bit integer:

```
127 * 16777216 + 0 * 65536 + 0 * 256 + 1 = 2130706433
```

Payload:
```
http://2130706433/flag
```

**Method 2: Hexadecimal IP notation**

```
http://0x7f000001/flag
```

**Method 3: Hex octets**

```
http://0x7f.0x0.0x0.0x1/flag
```

**Method 4: Octal notation**

```
http://0177.0.0.1/flag
```

**Method 5: Shortened IP (some HTTP clients accept this)**

```
http://127.1/flag
```

**Method 6: IPv6 mapped IPv4 (may work depending on the client)**

```
http://[::ffff:127.0.0.1]/flag
```

### Why This Works

String-based blacklists are fundamentally flawed because they cannot account for all possible representations of a network address. The loopback address `127.0.0.1` alone can be written in decimal, hexadecimal, octal, shortened, and mixed forms. The HTTP client library resolves these alternative notations correctly, so the request reaches the internal service despite the blacklist.

---

## Level 3 - Hard (Whitelist / Parser Quirks)

### Vulnerability

The backend enforces a whitelist: the URL **must** start with `http://trusted.breachpoint.io`. The check is a simple `str.startswith()` call.

The flaw lies in the difference between how the whitelist check interprets the URL (as a plain string) and how the HTTP client parses it (following the URL specification).

### Exploitation

The URL specification (RFC 3986) allows a **userinfo** component in the authority section:

```
http://userinfo@host:port/path
```

The `userinfo` part (before `@`) is treated as credentials, and the actual host the request goes to is the part **after** the `@`.

**Primary Payload:**

```
http://trusted.breachpoint.io@127.0.0.1/flag
```

**How it breaks down:**

| Component | Value |
|-----------|-------|
| Scheme | `http` |
| Userinfo | `trusted.breachpoint.io` |
| Host | `127.0.0.1` |
| Path | `/flag` |

The whitelist check sees the string starts with `http://trusted.breachpoint.io` and passes. But the HTTP client (`httpx`) parses the URL correctly according to the spec and sends the request to `127.0.0.1`, treating `trusted.breachpoint.io` as the username.

**Alternative Payload using fragment (`#`):**

```
http://trusted.breachpoint.io#@127.0.0.1/flag
```

Note: This variant may not work with all HTTP clients, as the fragment is typically not sent to the server. The `@` method is the most reliable.

### Expected Response

```json
{
  "flag": "FLAG{ssrf_m4st3r_0f_th3_1nt3rn4l_n3tw0rk}",
  "message": "You have successfully exploited SSRF to reach the internal service."
}
```

### Why This Works

The fundamental issue is a **TOCTOU (Time of Check, Time of Use)** mismatch:

1. **Time of Check:** The whitelist uses `str.startswith()`, which treats the URL as a flat string and sees `http://trusted.breachpoint.io` at the beginning.
2. **Time of Use:** The HTTP client parses the URL according to RFC 3986, interpreting `trusted.breachpoint.io` as userinfo (credentials) and `127.0.0.1` as the actual target host.

This class of vulnerability is known as a **URL parser differential** or **URL confusion** bug.

---

## Summary

| Level | Key Technique | Example Payload |
|-------|--------------|----------------|
| 1 | Direct access (no filter) | `http://127.0.0.1/flag` |
| 2 | Alternative IP encoding | `http://2130706433/flag` (decimal IP) |
| 3 | URL userinfo abuse | `http://trusted.breachpoint.io@127.0.0.1/flag` |

---

## Remediation Notes

For developers building real applications, here is how to properly defend against SSRF:

1. **Never rely on blacklists.** There are too many encoding tricks to block them all.
2. **Use allowlists of specific hosts/IPs** and validate the **resolved** IP address, not just the URL string.
3. **Parse the URL properly** before validation -- do not use string matching on raw URLs.
4. **Block private/internal IP ranges** (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8) at the network level or by resolving DNS and checking the result.
5. **Use a dedicated HTTP proxy** for outbound requests that enforces network policies.
6. **Disable unnecessary URL schemes** (file://, gopher://, dict://, etc.).
