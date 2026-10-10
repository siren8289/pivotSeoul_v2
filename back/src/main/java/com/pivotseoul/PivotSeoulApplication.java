package com.pivotseoul;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * pivotSeoul 백엔드 시작점.
 *
 * [요청 흐름]
 * React(front) → Spring(back, 이 서버) → FastAPI(ai)
 *                      ↓
 *                 DB(진단 기록 저장)
 */
@SpringBootApplication
public class PivotSeoulApplication {

    public static void main(String[] args) {
        SpringApplication.run(PivotSeoulApplication.class, args);
    }
}
