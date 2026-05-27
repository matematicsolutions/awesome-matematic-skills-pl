// Publiczne API silnika "Let It Be" (matematic-anonimizacja-pl).
//
// Samodzielny, RODO-safe, offline, zero zaleznosci. Logika polskich PII
// (PESEL/NIP/REGON/KRS + sygnatury sadow + imiona) pochodzi z wlasnej
// biblioteki MateMatic pl-entities (Patron). Patterny operacyjne (TTL,
// source_hash, audit log, AES-GCM) - cherry-pick z gregmos/PII-Shield (MIT).
// Atrybucja: THIRD_PARTY_INSPIRATIONS.md.

export { pseudonimizuj, anonimizuj, odwroc } from "./pseudonimizuj.mjs";
export { detect, countByType, PII_TYPES } from "./detect.mjs";
export { PL_EXTRACTION_RULES, detectAll, foldPl } from "./regex.mjs";
export {
    isValidPesel, isValidNip, isValidRegon, isValidRegon9, isValidRegon14,
    isValidKrsFormat, isValidIbanPl, isValidDowodOsobisty,
} from "./checksums.mjs";
export {
    MappingStore, sourceHash, encryptArchive, decryptArchive,
} from "./mapping-store.mjs";
export {
    AuditLog, ResidualPIIError, detectResidualPII, formatAuditLine,
} from "./audit-log.mjs";
export { POLISH_FIRST_NAMES, WSA_CITY_PREFIXES, COURTS } from "./gazetteers.mjs";
