package com.pivotseoul.recommend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.pivotseoul.ai.AiClient;
import com.pivotseoul.recommend.dto.RecommendRequest;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * 메인 기능 2: 예산에 맞는 자치구 추천
 * AI 서버가 25개 구의 예상 주거비를 계산하고, 이 서비스는 결과를 그대로 전달한다.
 */
@Service
public class RecommendService {

    private final AiClient aiClient;

    public RecommendService(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    public JsonNode recommend(RecommendRequest request) {
        Map<String, Object> body = new HashMap<>();
        body.put("life_stage", request.getLifeStage());
        body.put("house_type", request.getHouseType());
        body.put("area_m2", request.getAreaM2());
        body.put("building_age", request.getBuildingAge());
        body.put("floor", request.getFloor());
        body.put("monthly_income", request.getMonthlyIncome());
        return aiClient.recommend(body);
    }
}
