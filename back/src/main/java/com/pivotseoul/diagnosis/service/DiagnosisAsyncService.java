package com.pivotseoul.diagnosis.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.pivotseoul.ai.AiClient;
import com.pivotseoul.diagnosis.entity.Diagnosis;
import com.pivotseoul.diagnosis.repository.DiagnosisRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * 백그라운드에서 LLM(Gemini) 맞춤 설명을 비동기로 생성하고 진단 기록을 업데이트한다.
 * 메인 스레드의 진단 응답 시간을 0.1초 이내로 단축시키기 위한 비동기 처리 컴포넌트.
 */
@Service
public class DiagnosisAsyncService {

    private static final Logger log = LoggerFactory.getLogger(DiagnosisAsyncService.class);

    private final AiClient aiClient;
    private final DiagnosisRepository diagnosisRepository;

    public DiagnosisAsyncService(AiClient aiClient, DiagnosisRepository diagnosisRepository) {
        this.aiClient = aiClient;
        this.diagnosisRepository = diagnosisRepository;
    }

    @Async
    public void generateExplanationAsync(Long diagnosisId, Map<String, Object> userRequest, Map<String, Object> resultMetrics) {
        try {
            log.info("비동기 LLM 설명 생성 시작 - diagnosisId: {}", diagnosisId);
            Map<String, Object> payload = Map.of(
                    "request", userRequest,
                    "result", resultMetrics
            );
            JsonNode response = aiClient.explain(payload);

            String explanation = response.path("explanation").asText("");
            String source = response.path("explanation_source").asText("basic");

            Diagnosis diagnosis = diagnosisRepository.findById(diagnosisId).orElse(null);
            if (diagnosis != null) {
                diagnosis.setExplanation(explanation);
                diagnosis.setExplanationSource(source);
                diagnosis.setExplanationStatus("COMPLETED");
                diagnosisRepository.save(diagnosis);
                log.info("비동기 LLM 설명 생성 완료 - diagnosisId: {}, source: {}", diagnosisId, source);
            }
        } catch (Exception e) {
            log.warn("비동기 LLM 설명 생성 실패 (기본 설명 유지) - diagnosisId: {}, error: {}", diagnosisId, e.getMessage());
            Diagnosis diagnosis = diagnosisRepository.findById(diagnosisId).orElse(null);
            if (diagnosis != null && "PENDING".equals(diagnosis.getExplanationStatus())) {
                diagnosis.setExplanationStatus("FAILED");
                diagnosisRepository.save(diagnosis);
            }
        }
    }
}
