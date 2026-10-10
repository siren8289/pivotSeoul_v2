package com.pivotseoul.recommend.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.pivotseoul.recommend.dto.RecommendRequest;
import com.pivotseoul.recommend.service.RecommendService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * POST /api/recommendations   예산(소득의 30%) 안에 드는 자치구 추천
 */
@RestController
@RequestMapping("/api/recommendations")
public class RecommendController {

    private final RecommendService recommendService;

    public RecommendController(RecommendService recommendService) {
        this.recommendService = recommendService;
    }

    @PostMapping
    public JsonNode recommend(@Valid @RequestBody RecommendRequest request) {
        return recommendService.recommend(request);
    }
}
