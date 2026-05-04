// Tier 2 auto guard: 在 edit/write 前自动检查计划文件
export const WorkflowGuard = async ({ $, worktree, directory }) => {
  return {
    "tool.execute.before": async (input, output) => {
      const tool = input.tool;
      if (tool !== "edit" && tool !== "write" && tool !== "apply_patch") {
        return;
      }

      const filePath = output.args?.filePath || output.args?.file_path;
      if (!filePath) return;

      const guardScript = `${worktree}/.opencode/hooks/workflow_check.py`;
      const result = await $`python ${guardScript} --file ${filePath}`.nothrow();

      if (result.exitCode === 2) {
        throw new Error(
          `[Guard] BLOCKED: 没有找到今日计划文件。要修改源代码文件，请先创建计划。\n` +
          `   => 运行 /opsx:propose <feature-name> 或向 docs/plans/ 添加今日计划文件`
        );
      }
    },
  };
};
