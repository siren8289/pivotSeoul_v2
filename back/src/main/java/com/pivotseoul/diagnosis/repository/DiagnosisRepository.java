package com.pivotseoul.diagnosis.repository;

import com.pivotseoul.diagnosis.entity.Diagnosis;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/** 메서드 이름만 적으면 Spring Data JPA가 SQL을 만들어 준다. */
public interface DiagnosisRepository extends JpaRepository<Diagnosis, Long> {

    /** 최근 진단 10건 (최신순) */
    List<Diagnosis> findTop10ByOrderByIdDesc();
}
