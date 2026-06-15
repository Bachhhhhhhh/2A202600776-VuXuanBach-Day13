# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Cá nhân - Vũ Xuân Bách
- [REPO_URL]: https://github.com/Bachhhhhhhh/2A202600776-VuXuanBach-Day13
- [MEMBERS]:
  - Tên học viên: Vũ Xuân Bách | Role: Thực hiện toàn bộ Full-stack Observability (Logging, PII, Tracing, SLO, Alerts, Dashboard, Load Test, Incident Response, Report)

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 71 traces có tag `lab` trên Langfuse tại thời điểm kiểm chứng
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [docs/evidence/logging-correlation-pii.png](evidence/logging-correlation-pii.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [docs/evidence/logging-correlation-pii.png](evidence/logging-correlation-pii.png)
- [EVIDENCE_TRACE_LIST_SCREENSHOT]: [docs/evidence/langfuse-trace-list.png](evidence/langfuse-trace-list.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [docs/evidence/langfuse-trace-waterfall.png](evidence/langfuse-trace-waterfall.png)
- [TRACE_WATERFALL_EXPLANATION]: Trace incident [`f7f163eb01ade01e3afeaa3dfb4fe7db`](https://jp.cloud.langfuse.com/project/cmqevsbl7002cad0e84tzuud4/traces/f7f163eb01ade01e3afeaa3dfb4fe7db) có span cha `run` mất 5.652 giây. Span con `rag.retrieve` mất 5.501 giây (97.3% tổng latency), trong khi `llm.generate` chỉ mất 0.151 giây. Waterfall chứng minh nút thắt nằm ở retrieval sau khi bật incident `rag_slow`, không phải ở LLM.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [docs/evidence/dashboard-6-panels.png](evidence/dashboard-6-panels.png)
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 152ms |
| Error Rate | < 2% | 28d | 0.00% |
| Cost Budget | < $2.5/day | 1d | $0.0214 |

Dashboard dùng baseline sau remediation gồm 10 requests, quality average 0.88, 340 input tokens và 1,356 output tokens. Khi inject `rag_slow`, P95 đạt 5,653ms và vượt cả SLO 3,000ms lẫn alert threshold 5,000ms.

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [docs/evidence/alert-rules.png](evidence/alert-rules.png)
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md - High latency P95](alerts.md#1-high-latency-p95)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: Sau khi chạy `python scripts/inject_incident.py --scenario rag_slow`, client latency tăng từ khoảng 160-785ms lên 5.7-28.3 giây dưới concurrency 5. API metric ghi nhận P95 = 5,653ms; dashboard alert `high_latency_p95` chuyển sang `FIRING`. Error rate vẫn 0%, cho thấy đây là degradation về latency chứ không phải availability failure.
- [ROOT_CAUSE_PROVED_BY]: Langfuse Trace ID `f7f163eb01ade01e3afeaa3dfb4fe7db`, trong đó `rag.retrieve = 5.501s`, `llm.generate = 0.151s`, `run = 5.652s`. Log sự kiện `incident_enabled` xác nhận toggle `rag_slow=true`; correlation IDs của request incident gồm `req-10a2011d`, `req-838ebe71`, `req-6bfbbacc`, `req-7824e5b4` và `req-20e8065f`.
- [FIX_ACTION]: Đã chạy `python scripts/inject_incident.py --scenario rag_slow --disable` để khôi phục dịch vụ. Với production, đặt timeout cho retrieval, fallback sang nguồn/cache gần nhất và giới hạn concurrency để tránh request queue kéo dài.
- [PREVENTIVE_MEASURE]: Duy trì span riêng cho RAG/LLM, alert P95 > 5,000ms, SLO P95 < 3,000ms, synthetic probe định kỳ và runbook kiểm tra top slow traces. Thêm circuit breaker, cache retrieval và capacity/load test trước release.

---

## 5. Individual Contributions & Evidence

### Vũ Xuân Bách
- [TASKS_COMPLETED]: Hoàn thiện correlation ID, structured logging enrichment, PII scrubbing; sửa tích hợp Langfuse SDK v3 và JP host; thêm nested spans `rag.retrieve`/`llm.generate`; xây dashboard 6 panel refresh 15 giây; triển khai trang đánh giá 3 alert rules; chạy baseline/load test concurrency 5; inject và khắc phục `rag_slow`; phân tích trace/log/metrics; thu thập toàn bộ screenshot và hoàn thiện report.
- [EVIDENCE_LINK]: Implementation + evidence commit [`568cd76`](https://github.com/Bachhhhhhhh/2A202600776-VuXuanBach-Day13/commit/568cd76)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Theo dõi token input/output và estimated cost theo request; runbook đề xuất prompt shortening, model routing và cache. Evidence: panel Cost/Token trong `docs/evidence/dashboard-6-panels.png`.
- [BONUS_AUDIT_LOGS]: Không claim bonus; repo giữ sẵn `AUDIT_LOG_PATH` để mở rộng.
- [BONUS_CUSTOM_METRIC]: Có custom quality proxy `quality_avg` (baseline 0.88) với SLO threshold 0.75 và panel riêng trên dashboard.
