---
name: prototype-pollution-shield
description: Detects and mitigates JavaScript object prototype pollution vulnerabilities in untrusted JSON inputs and object merger routines.
agent: security-auditor
version: 1.0.0
---

# 🛡️ Prototype Pollution Shield Skill

## Objective
Enable an autonomous agent to inspect JavaScript/TypeScript object parsing, deep merge operations, and JSON decoders to ensure malicious payloads targeting `__proto__` or `constructor.prototype` cannot pollute the global object prototype.

## Threat Model
1. **Direct `__proto__` Injection:** Payloads specifying `"__proto__": { "polluted": true }`.
2. **Constructor Prototype Poisoning:** Nested payloads like `"constructor": { "prototype": { "polluted": true } }`.
3. **Over-zealous Blocking False Positives:** Ensuring safe property keys named `"constructor"` (e.g. `{"constructor": "Ford"}`) are parsed cleanly without throwing unexpected exceptions.

## Action Plan
1. **Static Review:** Audit `JSON.parse` reviver functions and recursive merge implementations.
2. **Payload Test:** Run targeted vectors verifying that modifying object properties does not leak to `Object.prototype`.
3. **Safe Mitigation:** Apply reviver checks or `Object.create(null)` dictionaries where applicable.
