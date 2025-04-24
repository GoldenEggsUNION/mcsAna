import os
import re
import datetime
import csv
from collections import defaultdict
import sys

def parse_log_time(date_str, time_str):
    """
    Combines date and time strings into a datetime object.

    Args:
        date_str (str): Date string in YYYY-MM-DD format.
        time_str (str): Time string in HH:MM:SS format.

    Returns:
        datetime.datetime: A datetime object representing the combined date and time.
                           Returns None if parsing fails.
    """
    datetime_str = f"{date_str} {time_str}"
    try:
        return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"警告: 无法解析日期时间字符串 '{datetime_str}'")
        return None

def consolidate_logs(source_dir, output_dir="date"):
    print(f"--- 开始日志文件合并 ---")
    if not os.path.isdir(source_dir):
        print(f"错误：源文件夹 '{source_dir}' 不存在。请检查路径。")
        print(f"--- 日志文件合并结束 (失败) ---")
        return False

    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"确保中间文件夹 '{output_dir}' 存在。")
    except OSError as e:
        print(f"创建中间文件夹 '{output_dir}' 失败: {e}")
        print(f"--- 日志文件合并结束 (失败) ---")
        return False

    log_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})-(\d+)\.log$')

    files_by_date = defaultdict(list)

    print(f"正在扫描源文件夹: {source_dir}")
    try:
        for entry_name in os.listdir(source_dir):
            full_path = os.path.join(source_dir, entry_name)

            if os.path.isfile(full_path):
                match = log_pattern.match(entry_name)
                if match:
                    date_str = match.group(1)
                    file_number = int(match.group(2))
                    files_by_date[date_str].append((file_number, full_path))
                    print(f"找到文件: {entry_name}")

    except OSError as e:
        print(f"错误：列出源文件夹 '{source_dir}' 中的文件失败: {e}")
        print(f"--- 日志文件合并结束 (失败) ---")
        return False

    if not files_by_date:
        print("在源文件夹中没有找到符合 'YYYY-MM-DD-N.log' 模式的日志文件。")
        print(f"--- 日志文件合并结束 (无文件可合并) ---")
        return True

    print(f"找到 {len(files_by_date)} 个不同日期的原始日志。")

    processed_dates_count = 0
    for date_str, files_list in sorted(files_by_date.items()):
        print(f"正在合并日期: {date_str} (共 {len(files_list)} 个文件)")

        files_list.sort(key=lambda item: item[0])

        output_filename = f"{date_str}.log"
        output_filepath = os.path.join(output_dir, output_filename)

        try:
            with open(output_filepath, 'w', encoding='utf-8') as outfile:
                print(f"  正在写入合并文件: {output_filepath}")
                for file_number, original_filepath in files_list:
                    print(f"    追加: {os.path.basename(original_filepath)}")
                    try:
                        with open(original_filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            if not content.endswith('\n'):
                                outfile.write('\n')
                            outfile.write(f"\n--- End of {os.path.basename(original_filepath)} ---\n\n") # Clear separator

                    except IOError as e:
                        print(f"    警告：读取原始文件 '{original_filepath}' 失败: {e}。跳过该文件。")
                    except Exception as e:
                         print(f"    警告：读取原始文件 '{original_filepath}' 时发生未知错误: {e}。跳过该文件。")

            processed_dates_count += 1

        except IOError as e:
            print(f"  错误：写入合并文件 '{output_filepath}' 失败: {e}。跳过该日期。")
        except Exception as e:
            print(f"  处理日期 {date_str} 时发生未知错误: {e}。跳过该日期。")


    print(f"成功合并了 {processed_dates_count} 个日期的日志。")
    print(f"--- 日志文件合并完成 ---")
    return True

def analyze_logs(date_dir="date", output_dir="view"):
    print(f"\n--- 开始日志文件分析 ---")
    if not os.path.isdir(date_dir):
        print(f"错误：合并日志文件夹 '{date_dir}' 不存在。请确保先执行合并步骤。")
        print(f"--- 日志文件分析结束 (失败) ---")
        return

    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"确保分析结果文件夹 '{output_dir}' 存在。")
    except OSError as e:
        print(f"创建分析结果文件夹 '{output_dir}' 失败: {e}")
        print(f"--- 日志文件分析结束 (失败) ---")
        return

    line_pattern = re.compile(r'^\[(\d{2}:\d{2}:\d{2})\] \[[^/]+/INFO\]: (.*)$')

    login_pattern = re.compile(r'^([a-zA-Z0-9_]+)\[/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\] logged in')
    logout_pattern = re.compile(r'^([a-zA-Z0-9_]+) left the game$')
    command_pattern = re.compile(r'^([a-zA-Z0-9_]+) issued server command:')

    log_files = [f for f in os.listdir(date_dir) if f.endswith(".log") and re.match(r'^\d{4}-\d{2}-\d{2}\.log$', f)]
    log_files.sort()

    if not log_files:
        print(f"在 '{date_dir}' 文件夹中没有找到符合 'YYYY-MM-DD.log' 模式的合并日志文件。")
        print(f"--- 日志文件分析结束 (无文件可分析) ---")
        return

    print(f"找到 {len(log_files)} 个需要分析的合并日志文件。")

    analyzed_dates_count = 0
    for log_filename in log_files:
        date_str = log_filename[:10]
        log_filepath = os.path.join(date_dir, log_filename)
        print(f"\n正在分析文件: {log_filepath}")

        player_sessions = {}
        player_total_online_time = defaultdict(datetime.timedelta)
        player_command_counts = defaultdict(int)

        last_timestamp = None

        try:
            with open(log_filepath, 'r', encoding='utf-8') as infile:
                for line in infile:
                    line = line.strip()
                    if not line or line.startswith('--- End of'):
                        continue

                    match = line_pattern.match(line)
                    if match:
                        time_str = match.group(1)
                        message_content = match.group(2)

                        current_timestamp = parse_log_time(date_str, time_str)

                        if current_timestamp:
                            last_timestamp = current_timestamp

                            login_match = login_pattern.match(message_content)
                            if login_match:
                                player_name = login_match.group(1)
                                if player_name not in player_sessions:
                                     player_sessions[player_name] = current_timestamp

                            logout_match = logout_pattern.match(message_content)
                            if logout_match:
                                player_name = logout_match.group(1)
                                if player_name in player_sessions:
                                    session_start_time = player_sessions.pop(player_name)
                                    duration = current_timestamp - session_start_time
                                    player_total_online_time[player_name] += duration

                            command_match = command_pattern.match(message_content)
                            if command_match:
                                 player_name = command_match.group(1)
                                 player_command_counts[player_name] += 1


        except IOError as e:
            print(f"错误：读取合并日志文件 '{log_filepath}' 失败: {e}。跳过该文件。")
            continue

        except Exception as e:
             print(f"分析文件 '{log_filepath}' 时发生未知错误: {e}。跳过该文件。")
             continue


        if player_sessions and last_timestamp:
            print(f"  处理文件结束时仍在线的玩家 ({len(player_sessions)}人)...")
            for player_name, login_time in list(player_sessions.items()):
                 duration = last_timestamp - login_time
                 player_total_online_time[player_name] += duration


        output_csv_filename = f"{date_str}_analysis.csv"
        output_csv_filepath = os.path.join(output_dir, output_csv_filename)

        all_players = sorted(set(player_total_online_time.keys()) | set(player_command_counts.keys()))

        if not all_players:
             print(f"  该日 ({date_str}) 没有玩家活动记录。")
             continue

        try:
            with open(output_csv_filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                csv_writer = csv.writer(csvfile)

                csv_writer.writerow([
                    "玩家",
                    "累计在线（秒）",
                    "累计在线（分）",
                    "累计在线（时）",
                    "累计使用命令（次）"
                ])

                print(f"  正在写入分析结果到 {output_csv_filepath}")
                for player_name in all_players:
                    total_timedelta = player_total_online_time.get(player_name, datetime.timedelta(0))
                    total_seconds = int(total_timedelta.total_seconds()) # Get total seconds as integer

                    total_minutes = total_seconds / 60.0
                    total_hours = total_seconds / 3600.0

                    command_count = player_command_counts.get(player_name, 0)

                    csv_writer.writerow([
                        player_name,
                        total_seconds,
                        round(total_minutes, 2),
                        round(total_hours, 2),
                        command_count
                    ])

            analyzed_dates_count += 1

        except IOError as e:
            print(f"错误：写入 CSV 文件 '{output_csv_filepath}' 失败: {e}")
        except Exception as e:
            print(f"生成 CSV 文件 '{output_csv_filepath}' 时发生未知错误: {e}")

    print(f"成功分析了 {analyzed_dates_count} 个日期的日志。")
    print(f"--- 日志文件分析完成 ---")


if __name__ == "__main__":
    original_logs_directory = "."
    consolidated_logs_directory = "date"
    analysis_output_directory = "view"

    print(">>> 开始执行日志整理和分析流程 <<<")

    consolidation_successful = consolidate_logs(original_logs_directory, consolidated_logs_directory)

    if consolidation_successful:
        analyze_logs(consolidated_logs_directory, analysis_output_directory)
    else:
        print("\n由于合并步骤失败，跳过分析。")


    print("\n>>> 日志整理和分析流程执行完毕 <<<")
