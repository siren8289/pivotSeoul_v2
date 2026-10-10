package com.pivotseoul.diagnosis.controller;

import com.pivotseoul.diagnosis.dto.DiagnosisRequest;
import com.pivotseoul.diagnosis.entity.Diagnosis;
import com.pivotseoul.diagnosis.service.DiagnosisService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * POST /api/diagnoses        진단 실행 + 저장
 * GET  /api/diagnoses/{id}   진단 결과 다시 보기
 * GET  /api/diagnoses        최근 진단 10건
 */
@RestController
@RequestMapping("/api/diagnoses")
public class DiagnosisController {

    private final DiagnosisService diagnosisService;

    public DiagnosisController(DiagnosisService diagnosisService) {
        this.diagnosisService = diagnosisService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Diagnosis create(@Valid @RequestBody DiagnosisRequest request) {
        return diagnosisService.diagnose(request);
    }

    @GetMapping("/{id}")
    public Diagnosis get(@PathVariable Long id) {
        return diagnosisService.get(id);
    }

    @GetMapping
    public List<Diagnosis> recent() {
        return diagnosisService.recent();
    }
}
