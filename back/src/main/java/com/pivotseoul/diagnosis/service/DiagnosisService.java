package com.pivotseoul.diagnosis.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.pivotseoul.ai.AiClient;
import com.pivotseoul.diagnosis.dto.DiagnosisRequest;
import com.pivotseoul.diagnosis.entity.Diagnosis;
import com.pivotseoul.diagnosis.repository.DiagnosisRepository;
import com.pivotseoul.global.exception.ApiException;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 메인 기능 1: 내 주거비 진단
 *   1. 프론트 입력을 AI 서버에 보낸다
 *   2. AI 결과를 DB에 저장한다
 *   3. 저장된 결과를 돌려준다
 */
@Service
public class DiagnosisService {

    private final AiClient aiClient;
    private final DiagnosisRepository diagnosisRepository;

    public DiagnosisService(AiClient aiClient, DiagnosisRepository diagnosisRepository) {
        this.aiClient = aiClient;
        this.diagnosisRepository = diagnosisRepository;
    }

    public Diagnosis diagnose(DiagnosisRequest request) {
        // 1) AI 서버 호출. Python은 snake_case(예: area_m2) 이름을 쓰기 때문에 이름을 맞춰서 보낸다.
        Map<String, Object> body = new HashMap<>();
        body.put("life_stage", request.getLifeStage());
        body.put("district", request.getDistrict());
        body.put("house_type", request.getHouseType());
        body.put("area_m2", request.getAreaM2());
        body.put("building_age", request.getBuildingAge());
        body.put("floor", request.getFloor());
        body.put("monthly_income", request.getMonthlyIncome());
        body.put("deposit", request.getDeposit());
        body.put("monthly_rent", request.getMonthlyRent());
        JsonNode ai = aiClient.diagnose(body);

        // 2) 사용자 입력값을 저장할 객체에 담는다.
        Diagnosis diagnosis = new Diagnosis();
        diagnosis.setLifeStage(request.getLifeStage());
        diagnosis.setDistrict(request.getDistrict());
        diagnosis.setHouseType(request.getHouseType());
        diagnosis.setAreaM2(request.getAreaM2());
        diagnosis.setBuildingAge(request.getBuildingAge());
        diagnosis.setFloor(request.getFloor());
        diagnosis.setMonthlyIncome(request.getMonthlyIncome());
        diagnosis.setDeposit(request.getDeposit());
        diagnosis.setMonthlyRent(request.getMonthlyRent());

        // 3) AI 결과를 담는다.
        diagnosis.setMonthlyCost(ai.path("monthly_cost").asDouble());
        diagnosis.setRirPercent(readNumber(ai, "rir_percent"));
        diagnosis.setStatus(ai.path("status").asText());
        diagnosis.setRedZone(ai.path("is_red_zone").asBoolean());
        diagnosis.setMlPrice(ai.path("ml_price").asDouble());
        diagnosis.setDlPrice(ai.path("dl_price").asDouble());
        diagnosis.setMarketPrice(ai.path("market_price").asDouble());
        diagnosis.setPriceGapPercent(ai.path("price_gap_percent").asDouble());
        diagnosis.setDistrictMedianCost(readNumber(ai, "district_median_cost"));
        diagnosis.setAuditCount(readInteger(ai, "audit_count"));
        diagnosis.setExplanation(ai.path("explanation").asText());
        diagnosis.setExplanationSource(ai.path("explanation_source").asText());

        // 4) DB에 저장하고, 저장된 결과(id 포함)를 돌려준다.
        return diagnosisRepository.save(diagnosis);
    }

    public Diagnosis get(Long id) {
        Diagnosis diagnosis = diagnosisRepository.findById(id).orElse(null);
        if (diagnosis == null) {
            throw ApiException.notFound("진단 기록이 없습니다. id=" + id);
        }
        return diagnosis;
    }

    public List<Diagnosis> recent() {
        return diagnosisRepository.findTop10ByOrderByIdDesc();
    }

    /** JSON 값이 숫자면 숫자를, 아니면(null 등) null을 돌려준다. */
    private Double readNumber(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNumber()) {
            return value.asDouble();
        }
        return null;
    }

    private Integer readInteger(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNumber()) {
            return value.asInt();
        }
        return null;
    }
}
