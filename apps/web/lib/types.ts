/**
 * The shapes the API returns, as this app reads them.
 *
 * Hand-written rather than generated: the API publishes an OpenAPI document and
 * a generator would be the better answer once the two move together often, but
 * a build step nobody runs is worse than a file somebody has to update. These
 * are only the fields the dashboards use — an extra field on the API breaks
 * nothing here.
 */

export type Session = {
  user_type: 'parent' | 'child';
  id: string;
  display_name: string;
};

export type ChildProfile = {
  id: string;
  pseudonym: string;
  display_name: string;
  status: 'pending' | 'active' | 'disabled';
};

export type ParentProfile = {
  id: string;
  email: string;
  family_code: string;
  display_name: string;
};

export type AssignedActivity = {
  code: string;
  title: string;
  kind: 'h5p' | 'phet' | 'video' | 'assessment';
  duration_minutes: number;
};

export type AssignmentStatus = 'assigned' | 'in_progress' | 'completed' | 'cancelled';

export type ChildAssignment = {
  id: string;
  status: AssignmentStatus;
  note: string | null;
  due_on: string | null;
  activity: AssignedActivity;
  assigned_at: string;
  started_at: string | null;
  completed_at: string | null;
};

export type ParentAssignment = ChildAssignment & {
  child_id: string;
  child_pseudonym: string;
  cancelled_at: string | null;
};

export type ActivityContent = {
  library_name: string;
  library_version: string;
  play_url: string;
  expires_in: number;
};

export type Outcome = 'mastered' | 'partial' | 'not_mastered';

export type CompetencyProgress = {
  competency_code: string;
  latest_outcome: Outcome;
  latest_at: string;
  first_at: string;
  attempts_counted: number;
  outcomes: { mastered: number; partial: number; not_mastered: number };
  answered_total: number;
  correct_total: number;
  explanation: string;
};

export type Progress = {
  child_id: string;
  attempts_completed: number;
  competencies: CompetencyProgress[];
  evidence: {
    statements_received: number;
    responses_declared: number;
    responses_from_runtime: number;
  };
  computed_at: string;
};

export type LocalizedGap = {
  competency_code: string;
  competency_label: string | null;
  domain_code: string | null;
  domain_label: string | null;
  outcome: Outcome;
  attempts_counted: number;
  answered: number;
  correct: number;
  rule_code: string;
  explanation: string;
  last_seen_at: string;
  blocked_by: string | null;
  deferral: string | null;
};

export type GeneralGap = {
  domain_code: string;
  domain_label: string;
  competency_codes: string[];
  rule_code: string;
  explanation: string;
};

export type RootCause = {
  competency_code: string;
  explains_codes: string[];
  rule_code: string;
  explanation: string;
  confirmed: boolean;
};

export type Health = {
  score: number;
  rule_code: string;
  observed: number;
  attempts: number;
  mastered: number;
  partial: number;
  not_mastered: number;
  explanation: string;
};

export type Recommendation = {
  competency_code: string;
  activity_code: string;
  title: string;
  kind: string;
  duration_minutes: number;
  already_done: boolean;
  reason: string;
  proof: string;
};

export type Diagnostic = {
  child_id: string;
  health: Health | null;
  localized_gaps: LocalizedGap[];
  general_gaps: GeneralGap[];
  root_causes: RootCause[];
  recommendations: Recommendation[];
  tree_available: boolean;
  computed_at: string;
};

export type NextStep = {
  activity_code: string;
  title: string;
  kind: string;
  duration_minutes: number;
};

export type AssessmentQuestion = {
  question_ref: string;
  prompt: string;
  choices: string[];
};

export type Assessment = {
  done: boolean;
  assignment_id: string | null;
  title: string | null;
  questions: AssessmentQuestion[];
};

export type NextSteps = { steps: NextStep[]; computed_at: string };

export type Attempt = {
  id: string;
  assignment_id: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  started_at: string;
  completed_at: string | null;
  responses: unknown[];
  results: {
    competency_code: string;
    outcome: Outcome;
    answered: number;
    correct: number;
    rule_code: string;
    explanation: string;
  }[];
};

export type AppliedRemediation = {
  assigned: string[];
  skipped: string[];
  reason: string;
};

export const OUTCOME_LABELS: Record<Outcome, string> = {
  mastered: 'acquise',
  partial: 'en cours d’acquisition',
  not_mastered: 'non acquise',
};

/**
 * How an outcome is coloured. Three bands and no gradient: a mark never replaces
 * a competency, and a continuous scale would read as one.
 */
export const OUTCOME_CLASSES: Record<Outcome, string> = {
  mastered: 'text-bg-success',
  partial: 'text-bg-warning',
  not_mastered: 'text-bg-secondary',
};
