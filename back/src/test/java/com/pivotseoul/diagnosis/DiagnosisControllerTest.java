package com.pivotseoul.diagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pivotseoul.ai.AiClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** AI 서버는 가짜(Mock)로 바꾸고, Spring의 저장·조회 흐름만 확인한다. */
@SpringBootTest
@AutoConfigureMockMvc
class DiagnosisControllerTest {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @MockBean
    AiClient aiClient;

    private static final String REQUEST = """
            {"lifeStage":"youth","district":"마포구","houseType":"officetel","areaM2":30,
             "buildingAge":10,"floor":5,"monthlyIncome":300,"deposit":1000,"monthlyRent":80}
            """;

    @Test
    void createAndGet() throws Exception {
        given(aiClient.diagnose(any())).willReturn(objectMapper.readTree("""
                {"monthly_cost":84.2,"rir_percent":28.1,"status":"stable","is_red_zone":false,
                 "ml_price":90.0,"dl_price":88.0,"market_price":89.0,"price_gap_percent":-5.4,
                 "district_median_cost":95.0,"audit_count":101,
                 "explanation":"안정 단계입니다.","explanation_source":"basic"}
                """));

        mockMvc.perform(post("/api/diagnoses").contentType(MediaType.APPLICATION_JSON).content(REQUEST))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.status").value("stable"))
                .andExpect(jsonPath("$.marketPrice").value(89.0));

        mockMvc.perform(get("/api/diagnoses"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].district").value("마포구"));
    }

    @Test
    void invalidIncomeReturns400() throws Exception {
        String bad = REQUEST.replace("\"monthlyIncome\":300", "\"monthlyIncome\":0");
        mockMvc.perform(post("/api/diagnoses").contentType(MediaType.APPLICATION_JSON).content(bad))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorCode").value("VALIDATION_ERROR"));
    }
}
